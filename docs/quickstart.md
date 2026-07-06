# Quick start

The example below is the **official aiogram quickstart**, ported to baleio almost
line-for-line. Only the import roots and the text formatter change — Bale renders
Markdown, so `md` replaces aiogram's `html`.

```python
import asyncio
import logging
import sys
from os import getenv

from baleio import Bot, Dispatcher, md
from baleio.client.default import DefaultBotProperties
from baleio.enums import ParseMode
from baleio.filters import CommandStart
from baleio.types import Message

TOKEN = getenv("BOT_TOKEN")   # get one from @botfather in Bale

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {md.bold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: Message) -> None:
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
```

Run it:

```bash
export BOT_TOKEN=123456:xxxxxxxx
python quickstart.py
```

## What just happened?

- **`Dispatcher`** is the root router. You attach handlers to it (or to a `Router` you
  include).
- **`@dp.message(CommandStart())`** registers a handler for the `/start` command.
- **`message.answer(...)`** is a shortcut that calls `sendMessage` for the same chat —
  the event is bound to its `Bot`, so you don't pass `bot` around.
- **`message.send_copy(...)`** re-sends the incoming message's content (text, photo,
  document, …) and raises `TypeError` for content Bale can't re-send.
- **`dp.start_polling(bot)`** starts long polling.

:::{admonition} Bale vs. Telegram
:class: note

Bale always renders **Markdown** and does not accept a `parse_mode` request
parameter. `DefaultBotProperties(parse_mode=...)` is accepted for aiogram parity and
safely ignored. Use {doc}`md <api>` helpers (`md.bold`, `md.italic`, `md.link`) for
formatting — note that Bale requires a space **before** and **after** `*` / `_`
markers, which the helpers handle for you.
:::

## Next steps

- {doc}`dispatcher` — routers, middlewares and dependency injection
- {doc}`filters` — `Command`, magic `F`, combinators
- {doc}`fsm` — multi-step conversations
- {doc}`keyboards` — inline & reply keyboards
