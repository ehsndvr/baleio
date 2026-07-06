"""The aiogram quickstart, ported to baleio almost line-for-line.

Compare with aiogram's official example — only the import roots and the text
formatter (Bale uses Markdown, so ``md`` instead of ``html``) change.
"""
import asyncio
import logging
import sys
from os import getenv

from baleio import Bot, Dispatcher, md
from baleio.client.default import DefaultBotProperties
from baleio.enums import ParseMode
from baleio.filters import CommandStart
from baleio.types import Message

# Bot token can be obtained via @botfather in Bale
TOKEN = getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """This handler receives messages with the `/start` command."""
    # Most event objects have aliases for API methods that can be called in
    # the event's context — e.g. `message.answer(...)` sends to the same chat,
    # or call the API directly via `bot.send_message(chat_id=..., ...)`.
    await message.answer(f"Hello, {md.bold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: Message) -> None:
    """Forward the received message back to the sender.

    A bare `@dp.message()` handles every message type (text, photo, ...).
    """
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # Not every content type can be copied, so handle that
        await message.answer("Nice try!")


async def main() -> None:
    # Bale ignores parse_mode (it always renders Markdown), but DefaultBotProperties
    # is accepted for full aiogram parity.
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
