"""The Dispatcher — root router, update feeder and polling loop."""
from __future__ import annotations

import asyncio
import contextlib
import logging
from typing import Any, Optional

from ..client.bot import Bot
from ..fsm.context import FSMContext
from ..fsm.storage.base import BaseStorage, StorageKey
from ..fsm.storage.memory import MemoryStorage
from ..types import Update
from ..types.base import bot_context
from ..types.error import ErrorEvent
from .event.observer import UNHANDLED
from .router import Router

logger = logging.getLogger("baleio.dispatcher")


class Dispatcher(Router):
    """Root router. Owns the FSM storage and drives update processing."""

    def __init__(
        self,
        storage: Optional[BaseStorage] = None,
        name: str = "dispatcher",
        **workflow_data: Any,
    ) -> None:
        super().__init__(name=name)
        self.storage = storage or MemoryStorage()
        self.workflow_data: dict[str, Any] = workflow_data
        self._running = False
        self._stop_event: Optional[asyncio.Event] = None

    def __getitem__(self, key: str) -> Any:
        return self.workflow_data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.workflow_data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.workflow_data.get(key, default)

    # --- FSM key derivation ------------------------------------------------
    @staticmethod
    def _resolve_ids(update: Update) -> Optional[tuple[int, int]]:
        """Return ``(chat_id, user_id)`` used to key FSM storage."""
        message = update.message or update.edited_message
        if message is not None:
            chat_id = message.chat.id
            user_id = message.from_user.id if message.from_user else chat_id
            return chat_id, user_id
        if update.callback_query is not None:
            cq = update.callback_query
            user_id = cq.from_user.id if cq.from_user else 0
            chat_id = cq.message.chat.id if cq.message else user_id
            return chat_id, user_id
        if update.pre_checkout_query is not None:
            pcq = update.pre_checkout_query
            user_id = pcq.from_user.id if pcq.from_user else 0
            return user_id, user_id
        return None

    def fsm_context(self, bot: Bot, chat_id: int, user_id: int) -> FSMContext:
        key = StorageKey(bot_id=bot.id, chat_id=chat_id, user_id=user_id)
        return FSMContext(storage=self.storage, key=key)

    # --- feeding -----------------------------------------------------------
    async def feed_update(self, bot: Bot, update: Update, **extra: Any) -> Any:
        """Process a single already-parsed :class:`Update`."""
        bot._bind(update)
        event_type = update.event_type
        event = update.event
        if event is None:
            logger.debug("Skipping update %s with no known event", update.update_id)
            return UNHANDLED

        data: dict[str, Any] = {
            "bot": bot,
            "event_update": update,
            "update": update,
            "event_type": event_type,
            event_type: event,
            **self.workflow_data,
            **extra,
        }

        ids = self._resolve_ids(update)
        if ids is not None:
            state = self.fsm_context(bot, *ids)
            data["state"] = state
            data["raw_state"] = await state.get_state()

        token = bot_context.set(bot)
        try:
            try:
                return await self.propagate_event(event_type, event, data)
            except Exception as exception:  # noqa: BLE001
                return await self._propagate_error(bot, update, exception, data)
        finally:
            bot_context.reset(token)

    async def _propagate_error(
        self, bot: Bot, update: Update, exception: Exception, data: dict[str, Any]
    ) -> Any:
        """Route an exception to ``errors`` handlers; re-raise if unhandled."""
        error_event = bot._bind(ErrorEvent(update=update, exception=exception))
        error_data = {**data, "event_update": update, "exception": exception}
        result = await self.propagate_event("error", error_event, error_data)
        if result is UNHANDLED:
            raise exception
        return result

    async def feed_raw_update(self, bot: Bot, raw: dict[str, Any], **extra: Any) -> Any:
        return await self.feed_update(bot, Update.model_validate(raw), **extra)

    # --- polling -----------------------------------------------------------
    async def start_polling(
        self,
        *bots: Bot,
        polling_timeout: int = 30,
        limit: int = 100,
        handle_as_tasks: bool = True,
        drop_pending_updates: bool = False,
        on_startup: Optional[Any] = None,
        on_shutdown: Optional[Any] = None,
    ) -> None:
        """Long-poll ``getUpdates`` for one or more bots until stopped."""
        if not bots:
            raise ValueError("start_polling requires at least one Bot")
        self._running = True
        self._stop_event = asyncio.Event()

        if on_startup is not None:
            await on_startup(*bots)

        try:
            for bot in bots:
                me = await bot.get_me()
                logger.info("Start polling for bot @%s (id=%s)", me.username, me.id)
            tasks = [
                asyncio.create_task(
                    self._poll_bot(
                        bot,
                        polling_timeout=polling_timeout,
                        limit=limit,
                        handle_as_tasks=handle_as_tasks,
                        drop_pending_updates=drop_pending_updates,
                    )
                )
                for bot in bots
            ]
            await self._stop_event.wait()
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
        finally:
            self._running = False
            if on_shutdown is not None:
                await on_shutdown(*bots)
            for bot in bots:
                with contextlib.suppress(Exception):
                    await bot.close()

    async def _poll_bot(
        self,
        bot: Bot,
        polling_timeout: int,
        limit: int,
        handle_as_tasks: bool,
        drop_pending_updates: bool,
    ) -> None:
        offset: Optional[int] = None
        if drop_pending_updates:
            # a negative offset asks the server to forget queued updates
            with contextlib.suppress(Exception):
                await bot.get_updates(offset=-1, timeout=0)
            offset = None

        background: set[asyncio.Task] = set()
        backoff = 1.0
        while self._running:
            try:
                updates = await bot.get_updates(
                    offset=offset, limit=limit, timeout=polling_timeout
                )
                backoff = 1.0
            except asyncio.CancelledError:
                raise
            except Exception as error:  # noqa: BLE001
                logger.error("getUpdates failed: %r; retrying in %.1fs", error, backoff)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30.0)
                continue

            for update in updates:
                offset = update.update_id + 1
                if handle_as_tasks:
                    task = asyncio.create_task(self._safe_feed(bot, update))
                    background.add(task)
                    task.add_done_callback(background.discard)
                else:
                    await self._safe_feed(bot, update)

    async def _safe_feed(self, bot: Bot, update: Update) -> None:
        """Feed one update, logging (not raising) handler errors so polling survives."""
        try:
            await self.feed_update(bot, update)
        except Exception:  # noqa: BLE001
            logger.exception("Error while handling update %s", update.update_id)

    def stop_polling(self) -> None:
        if self._stop_event is not None:
            self._stop_event.set()

    def run_polling(self, *bots: Bot, **kwargs: Any) -> None:
        """Blocking convenience wrapper around :meth:`start_polling`."""
        try:
            asyncio.run(self.start_polling(*bots, **kwargs))
        except (KeyboardInterrupt, SystemExit):
            logger.info("Polling stopped")
