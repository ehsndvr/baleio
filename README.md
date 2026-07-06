<div align="center">

# baleio

**A modern, fully-async framework for [Bale](https://bale.ai) (بله) bots — inspired by [aiogram](https://github.com/aiogram/aiogram).**

[![CI](https://github.com/ehsndvr/baleio/actions/workflows/ci.yml/badge.svg)](https://github.com/ehsndvr/baleio/actions/workflows/ci.yml)
[![Docs](https://github.com/ehsndvr/baleio/actions/workflows/docs.yml/badge.svg)](https://ehsndvr.github.io/baleio/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![Pydantic v2](https://img.shields.io/badge/pydantic-v2-e92063)](https://docs.pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

[**Documentation**](https://ehsndvr.github.io/baleio/) · [**Quick start**](#quick-start) · [**Examples**](examples/) · [**فارسی 🇮🇷**](README.fa.md)

</div>

---

If you have ever worked with `aiogram`, you already know `baleio`. Same architecture,
same patterns — this time for the **Bale bot API** (`https://tapi.bale.ai`). Routers,
magic filters, FSM, dependency injection, keyboard builders, callback-data factories
and centralized error handling all work the way you expect.

## Features

- ⚡️ **Fully asynchronous** on top of `aiohttp`.
- 🧩 **`Dispatcher` / `Router`** with nested routing and per-event observers.
- 🎯 **Filters**: `Command`, `CommandStart`, `StateFilter`, the magic filter `F`, plain
  callables, and `&` / `|` / `~` combinators.
- 🏷️ **`CallbackData` factory** — type-safe, packed/unpacked structured callback payloads.
- 💾 **Finite State Machine** with `StatesGroup` / `State` and pluggable storage (`MemoryStorage`).
- ⌨️ **Keyboard builders** for inline and reply keyboards.
- 🧱 **Pydantic v2 models** for every Bale API type.
- 🔌 **Middlewares** at the event level (inner & outer).
- 🧯 **Centralized error handling** via `@dp.errors()` and `ErrorEvent`.
- 📎 File uploads (`multipart/form-data`), sending by `file_id` or URL, and media groups.
- 💳 Wallet payments (`sendInvoice`, `PreCheckoutQuery`, `answerPreCheckoutQuery`, …).
- 🪝 Long polling **and** webhook support.

## Installation

```bash
pip install baleio          # once published to PyPI
# or, from source:
git clone https://github.com/ehsndvr/baleio && cd baleio
pip install -e .
```

**Requirements:** Python 3.9+, `aiohttp`, `pydantic>=2`, `magic-filter`.

## Quick start

The snippet below is the **official aiogram quickstart**, ported to `baleio` almost
line-for-line. Only the import roots and the text formatter change (Bale renders
Markdown, so `md` replaces aiogram's `html`).

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

> **Compatibility note:** Bale does not accept a `parse_mode` request parameter (it
> always renders Markdown), but `DefaultBotProperties(parse_mode=...)` is accepted for
> full aiogram parity and safely ignored. Use `md` for bold/italic/link formatting.

## Core concepts

### The Bot client

```python
bot = Bot("123456:TOKEN")

me = await bot.get_me()
await bot.send_message(chat_id, "Hello")
await bot.send_photo(chat_id, "https://example.com/pic.jpg", caption="A photo")
await bot.send_photo(chat_id, FSInputFile("local.jpg"))      # upload from disk
await bot.edit_message_text(chat_id, message_id, "New text")
await bot.delete_message(chat_id, message_id)
```

Every documented Bale method is implemented: `sendMessage`, `forwardMessage`,
`copyMessage`, `sendPhoto/Audio/Document/Video/Animation/Voice`, `sendMediaGroup`,
`sendLocation`, `sendContact`, `sendChatAction`, `getFile`, `answerCallbackQuery`,
`askReview`, chat administration (`banChatMember`, `promoteChatMember`, `getChat`,
`getChatAdministrators`, `pinChatMessage`, …), message editing/deletion, stickers,
and payments (`sendInvoice`, `createInvoiceLink`, `answerPreCheckoutQuery`,
`inquireTransaction`).

### Dispatcher & Router

```python
from baleio import Dispatcher, Router
from baleio.filters import Command

dp = Dispatcher()
admin = Router(name="admin")
dp.include_router(admin)

@dp.message(Command("start"))
async def start(message): ...

@admin.message(Command("ban"))
async def ban(message): ...
```

Handlers are checked in registration order; the first whose filters all pass runs.

### Dependency injection

Each handler receives the event as its first argument. Remaining parameters are
filled **by name** from the propagated context:

```python
@dp.message(Command("me"))
async def me(message: Message, bot: Bot, state: FSMContext):
    ...   # bot and state are injected automatically
```

Available keys: `bot`, `state`, `raw_state`, `event_update` (the `Update`),
`event_router`, and anything a filter returned (e.g. `command`).

### Filters

```python
from baleio.filters import Command, CommandStart, StateFilter, F

@dp.message(Command("help"))                          # /help
@dp.message(CommandStart())                           # /start
@dp.message(F.text == "hello")                        # magic filter
@dp.message(F.text.startswith("/"))
@dp.message(F.from_user.id == 12345)
@dp.message(lambda m: m.text and len(m.text) > 100)   # plain callable
@dp.message(Command("go") & (F.from_user.id == 42))   # combinators
```

`Command` also injects a `CommandObject`:

```python
@dp.message(Command("say"))
async def say(message: Message, command: CommandObject):
    await message.answer(command.args or "Say what?")
```

### CallbackData factory

Type-safe, structured callback payloads — exactly like aiogram:

```python
from baleio import F
from baleio.filters import CallbackData
from baleio.types import CallbackQuery
from baleio.utils import InlineKeyboardBuilder

class Vote(CallbackData, prefix="vote"):     # optional: prefix="v", sep="|"
    action: str
    post_id: int

kb = (
    InlineKeyboardBuilder()
    .button("👍", callback_data=Vote(action="up", post_id=7).pack())     # -> "vote:up:7"
    .button("👎", callback_data=Vote(action="down", post_id=7).pack())
    .as_markup()
)

@dp.callback_query(Vote.filter(F.action == "up"))
async def upvote(query: CallbackQuery, callback_data: Vote):
    await query.answer(f"Post {callback_data.post_id} liked")
```

Fields are coerced back to their declared types on `unpack` (`post_id` is an `int`),
and Bale's 64-byte `callback_data` limit is enforced automatically.

### Finite State Machine

```python
from baleio.fsm import State, StatesGroup, FSMContext

class Form(StatesGroup):
    name = State()
    age = State()

@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.set_state(Form.name)
    await message.answer("What's your name?")

@dp.message(Form.name)                       # a State used directly as a filter
async def got_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Form.age)
    await message.answer("How old are you?")
```

### Keyboards

```python
from baleio.utils import InlineKeyboardBuilder

kb = (
    InlineKeyboardBuilder()
    .button("Yes", callback_data="yes")
    .button("No", callback_data="no")
    .adjust(2)
    .as_markup()
)
await message.answer("Agree?", reply_markup=kb)

@dp.callback_query(F.data == "yes")
async def yes(cb):
    await cb.answer("Great!", show_alert=True)
    await cb.message.edit_text("You chose: Yes")
```

> ⚠️ You must call `answerCallbackQuery` (or `cb.answer()`) to release the button.

### Centralized error handling

If a handler raises, an `ErrorEvent` is routed to `@dp.errors()` handlers:

```python
from baleio.filters import ExceptionTypeFilter
from baleio.types import ErrorEvent

@dp.errors(ExceptionTypeFilter(ValueError))
async def on_value_error(event: ErrorEvent):
    await event.update.message.answer("Something went wrong 😔")

@dp.errors()   # any other unhandled error
async def on_any_error(event: ErrorEvent):
    logging.exception("Unhandled", exc_info=event.exception)
```

If no error handler matches, the exception is re-raised (logged in polling, so the bot
stays alive; handled by you in webhook mode).

### Shortcut methods

Every received object is bound to its `Bot`, so you never pass `bot` around:

```python
await message.answer("...")          # sendMessage to the same chat
await message.reply("...")           # reply (reply_to_message_id)
await message.answer_photo(photo)
await message.send_copy(chat_id)     # content-aware copy
await message.edit_text("...")
await message.delete()
await callback.answer("...")
await callback.message.edit_text("...")
```

## Receiving updates

### Long polling

```python
await dp.start_polling(bot)                        # async
dp.run_polling(bot)                                # blocking (wraps asyncio.run)
await dp.start_polling(bot, drop_pending_updates=True)
```

### Webhook

```python
from aiohttp import web
from baleio.types import Update

async def handler(request):
    await dp.feed_update(bot, Update.model_validate(await request.json()))
    return web.Response()
```

See [`examples/webhook_bot.py`](examples/webhook_bot.py).

## Examples

- [`examples/quickstart.py`](examples/quickstart.py) — the aiogram quickstart, ported.
- [`examples/echo_bot.py`](examples/echo_bot.py) — echo + inline keyboard + callbacks.
- [`examples/fsm_form_bot.py`](examples/fsm_form_bot.py) — a registration form with FSM.
- [`examples/webhook_bot.py`](examples/webhook_bot.py) — receiving updates via webhook.

```bash
export BOT_TOKEN=123456:xxxxxxxx
python examples/echo_bot.py
```

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## aiogram → baleio cheat sheet

| aiogram | baleio |
|---|---|
| `from aiogram import Bot, Dispatcher, F` | `from baleio import Bot, Dispatcher, F` |
| `aiogram.types.Message` | `baleio.types.Message` |
| `aiogram.filters.Command` | `baleio.filters.Command` |
| `aiogram.filters.callback_data.CallbackData` | `baleio.filters.CallbackData` |
| `aiogram.fsm.state.StatesGroup` | `baleio.fsm.StatesGroup` |
| `@dp.errors()` + `ErrorEvent` | `@dp.errors()` + `baleio.types.ErrorEvent` |
| `dp.start_polling(bot)` | `dp.start_polling(bot)` |
| `InlineKeyboardBuilder` | `baleio.utils.InlineKeyboardBuilder` |
| `aiogram.html.bold` | `baleio.md.bold` (Bale is Markdown-only) |

**Key differences from Telegram/aiogram:** Bale has no `parse_mode` parameter (always
Markdown), its updates are limited to `message`, `edited_message`, `callback_query`
and `pre_checkout_query`, and payments are wallet-only.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) and open an
issue or pull request.

## License

[MIT](LICENSE) © baleio contributors.

> **Disclaimer:** `baleio` is an independent, community project and is not affiliated
> with or endorsed by Bale Messenger or the aiogram project.
