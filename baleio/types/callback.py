from __future__ import annotations

from typing import Any, Optional

from pydantic import AliasChoices, Field

from .base import BaleObject
from .message import Message
from .user import User


class CallbackQuery(BaleObject):
    """An incoming callback query from an inline keyboard button."""

    id: str
    from_user: Optional[User] = Field(
        default=None, validation_alias=AliasChoices("from_user", "from")
    )
    message: Optional[Message] = None
    data: Optional[str] = None

    async def answer(
        self,
        text: Optional[str] = None,
        show_alert: Optional[bool] = None,
    ) -> bool:
        """Answer this callback query (always call it to release the button)."""
        return await self.bot.answer_callback_query(
            self.id, text=text, show_alert=show_alert
        )

    # convenience proxies to the attached message ---------------------------
    async def edit_text(self, text: str, **kwargs: Any) -> Any:
        if self.message is None:
            raise RuntimeError("callback query has no attached message")
        return await self.message.edit_text(text, **kwargs)

    async def edit_reply_markup(self, reply_markup: Any = None) -> Any:
        if self.message is None:
            raise RuntimeError("callback query has no attached message")
        return await self.message.edit_reply_markup(reply_markup)
