"""baleio — a modern, fully async framework for Bale (بله) bots.

Inspired by aiogram. Quick start::

    import asyncio
    from baleio import Bot, Dispatcher
    from baleio.filters import Command
    from baleio.types import Message

    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start(message: Message):
        await message.answer("سلام! به baleio خوش اومدی.")

    async def main():
        bot = Bot("TOKEN")
        await dp.start_polling(bot)

    asyncio.run(main())
"""
from __future__ import annotations

from . import enums, filters, types
from .__meta__ import __version__
from .client import AiohttpSession, BaseSession, Bot, DefaultBotProperties
from .dispatcher import Dispatcher, Router
from .exceptions import (
    BaleAPIError,
    BaleBadRequest,
    BaleError,
    BaleForbidden,
    BaleNetworkError,
    BaleNotFound,
    BaleRetryAfter,
    BaleUnauthorized,
)
from .filters import (
    CallbackData,
    Command,
    CommandStart,
    ExceptionTypeFilter,
    F,
    StateFilter,
)
from .fsm import FSMContext, MemoryStorage, State, StatesGroup
from .utils import InlineKeyboardBuilder, ReplyKeyboardBuilder
from .utils import markdown as md

#: Bale renders Markdown only, so ``md`` is the analogue of aiogram's ``html``.
markdown = md

__all__ = [
    "__version__",
    # sub-packages
    "types",
    "enums",
    "filters",
    "md",
    "markdown",
    # client
    "Bot",
    "DefaultBotProperties",
    "AiohttpSession",
    "BaseSession",
    # dispatcher
    "Dispatcher",
    "Router",
    # filters
    "F",
    "Command",
    "CommandStart",
    "StateFilter",
    "CallbackData",
    "ExceptionTypeFilter",
    # fsm
    "FSMContext",
    "State",
    "StatesGroup",
    "MemoryStorage",
    # keyboards
    "InlineKeyboardBuilder",
    "ReplyKeyboardBuilder",
    # exceptions
    "BaleError",
    "BaleAPIError",
    "BaleBadRequest",
    "BaleForbidden",
    "BaleNotFound",
    "BaleUnauthorized",
    "BaleNetworkError",
    "BaleRetryAfter",
]
