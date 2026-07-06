"""A minimal echo bot.

    export BALE_TOKEN=123456:xxxxxxxx
    python examples/echo_bot.py
"""
from __future__ import annotations

import asyncio
import logging
import os

from baleio import Bot, Dispatcher, F
from baleio.filters import CommandStart
from baleio.types import Message
from baleio.utils import InlineKeyboardBuilder

dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message) -> None:
    kb = (
        InlineKeyboardBuilder()
        .button("سلام بده 👋", callback_data="hi")
        .button("درباره", callback_data="about")
        .adjust(2)
        .as_markup()
    )
    await message.answer(
        f"سلام {message.from_user.first_name}! به baleio خوش اومدی.",
        reply_markup=kb,
    )


@dp.callback_query(F.data == "hi")
async def say_hi(callback) -> None:
    await callback.answer("سلام! 🌟", show_alert=True)


@dp.callback_query(F.data == "about")
async def about(callback) -> None:
    await callback.answer()
    await callback.message.answer("این بات با کتابخانه baleio ساخته شده.")


@dp.message(F.text)
async def echo(message: Message) -> None:
    await message.answer(message.text)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    token = os.environ["BALE_TOKEN"]
    bot = Bot(token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
