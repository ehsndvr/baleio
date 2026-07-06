<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="icons/lockup-primary-dark.svg">
  <img alt="baleio" src="icons/lockup-primary.svg" width="360">
</picture>

<br>

**یک فریم‌ورک مدرن و کاملاً async برای ساخت بازوهای [بله](https://bale.ai) — با الهام از [aiogram](https://github.com/aiogram/aiogram).**

[![CI](https://github.com/ehsndvr/baleio/actions/workflows/ci.yml/badge.svg)](https://github.com/ehsndvr/baleio/actions/workflows/ci.yml)
[![Docs](https://github.com/ehsndvr/baleio/actions/workflows/docs.yml/badge.svg)](https://ehsndvr.github.io/baleio/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![Pydantic v2](https://img.shields.io/badge/pydantic-v2-e92063)](https://docs.pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

[**مستندات**](https://ehsndvr.github.io/baleio/) · [**شروع سریع**](#شروع-سریع) · [**نمونه‌ها**](examples/) · [**English 🇬🇧**](README.md)

</div>

---

اگر با `aiogram` کار کرده‌اید، با `baleio` هم راحت هستید. همان معماری، همان الگوها —
این بار برای **API بازوی بله** (`https://tapi.bale.ai`). راوترها، فیلترهای جادویی، FSM،
تزریق وابستگی، کیبورد بیلدر، CallbackData factory و مدیریت خطای متمرکز، همگی دقیقاً همان‌طور
که انتظار دارید کار می‌کنند.

## ویژگی‌ها

- ⚡️ **کاملاً async** روی `aiohttp`
- 🧩 **`Dispatcher` / `Router`** با مسیریابی تودرتو و observer برای هر رویداد
- 🎯 **فیلترها**: `Command`, `CommandStart`, `StateFilter`، فیلتر جادویی `F`، توابع ساده و ترکیب با `&` / `|` / `~`
- 🏷️ **`CallbackData` factory** — داده‌ی callback ساخت‌یافته و type-safe
- 💾 **ماشین حالت (FSM)** با `StatesGroup` / `State` و ذخیره‌ساز `MemoryStorage`
- ⌨️ **کیبورد بیلدر** برای اینلاین و ریپلای
- 🧱 **مدل‌های Pydantic v2** برای همه‌ی تایپ‌های API بله
- 🔌 **middleware** در سطح رویداد (inner و outer)
- 🧯 **مدیریت خطای متمرکز** با `@dp.errors()` و `ErrorEvent`
- 📎 آپلود فایل با `multipart/form-data`، ارسال با `file_id` یا URL، و `sendMediaGroup`
- 💳 پرداخت کیف‌پولی (`sendInvoice`, `PreCheckoutQuery`, ...)
- 🪝 پشتیبانی از polling و webhook

## نصب

```bash
pip install baleio          # پس از انتشار روی PyPI
# یا از سورس:
git clone https://github.com/ehsndvr/baleio && cd baleio
pip install -e .
```

نیازمندی‌ها: Python 3.9+، `aiohttp`، `pydantic>=2`، `magic-filter`.

## شروع سریع

کد زیر **همان quickstart رسمی aiogram** است که تقریباً خط‌به‌خط به baleio پورت شده؛ فقط
ریشه‌ی import‌ها و فرمت‌کننده‌ی متن (بله Markdown است، پس `md` به‌جای `html`) عوض شده:

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

TOKEN = getenv("BOT_TOKEN")   # توکن را از @botfather بگیرید

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

> نکته‌ی سازگاری: بله پارامتر `parse_mode` را نمی‌گیرد (همیشه Markdown)، ولی
> `DefaultBotProperties(parse_mode=...)` برای سازگاری کامل با aiogram پذیرفته و بی‌خطر
> نادیده گرفته می‌شود. برای متن بولد/ایتالیک/لینک از `md` استفاده کنید.

## مفاهیم اصلی

### Bot — کلاینت API

```python
bot = Bot("123456:TOKEN")

me = await bot.get_me()
await bot.send_message(chat_id, "متن پیام")
await bot.send_photo(chat_id, "https://example.com/pic.jpg", caption="عکس")
await bot.send_photo(chat_id, FSInputFile("local.jpg"))     # آپلود از فایل
await bot.edit_message_text(chat_id, message_id, "متن جدید")
await bot.delete_message(chat_id, message_id)
```

همه‌ی متدهای مستندات بله پیاده‌سازی شده‌اند: `sendMessage`, `forwardMessage`, `copyMessage`,
`sendPhoto/Audio/Document/Video/Animation/Voice`, `sendMediaGroup`, `sendLocation`,
`sendContact`, `sendChatAction`, `getFile`, `answerCallbackQuery`, `askReview`، مدیریت چت،
ویرایش/حذف پیام، استیکرها، و پرداخت کیف‌پولی.

### Dispatcher و Router

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

هندلرها بر اساس ترتیب ثبت بررسی می‌شوند؛ اولین هندلری که همه‌ی فیلترهایش pass شوند اجرا می‌شود.

### تزریق وابستگی (Dependency Injection)

هر هندلر رویداد را به‌عنوان اولین آرگومان می‌گیرد و بقیه‌ی پارامترها بر اساس **نام** پر می‌شوند:

```python
@dp.message(Command("me"))
async def me(message: Message, bot: Bot, state: FSMContext):
    ...   # bot و state خودکار تزریق می‌شوند
```

### CallbackData factory

```python
from baleio import F
from baleio.filters import CallbackData
from baleio.types import CallbackQuery
from baleio.utils import InlineKeyboardBuilder

class Vote(CallbackData, prefix="vote"):     # می‌توانید sep هم بدهید: prefix="v", sep="|"
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
    await query.answer(f"پست {callback_data.post_id} لایک شد")
```

فیلدها هنگام `unpack` به تایپ درست تبدیل می‌شوند و محدودیت ۶۴ بایتی callback_data بله خودکار بررسی می‌شود.

### ماشین حالت (FSM)

```python
from baleio.fsm import State, StatesGroup, FSMContext

class Form(StatesGroup):
    name = State()
    age = State()

@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.set_state(Form.name)
    await message.answer("اسمت چیه؟")

@dp.message(Form.name)                    # State مستقیماً به‌عنوان فیلتر
async def got_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Form.age)
    await message.answer("چند سالته؟")
```

### کیبوردها

```python
from baleio.utils import InlineKeyboardBuilder

kb = (
    InlineKeyboardBuilder()
    .button("بله", callback_data="yes")
    .button("خیر", callback_data="no")
    .adjust(2)
    .as_markup()
)
await message.answer("موافقی؟", reply_markup=kb)

@dp.callback_query(F.data == "yes")
async def yes(cb):
    await cb.answer("عالی!", show_alert=True)
    await cb.message.edit_text("انتخاب شد: بله")
```

> ⚠️ فراخوانی `answerCallbackQuery` (یا `cb.answer()`) برای خارج‌کردن دکمه از حالت انتظار الزامی است.

### مدیریت خطای متمرکز

```python
from baleio.filters import ExceptionTypeFilter
from baleio.types import ErrorEvent

@dp.errors(ExceptionTypeFilter(ValueError))
async def on_value_error(event: ErrorEvent):
    await event.update.message.answer("یه مشکلی پیش اومد 😔")

@dp.errors()   # هر خطای مدیریت‌نشده‌ی دیگر
async def on_any_error(event: ErrorEvent):
    logging.exception("Unhandled", exc_info=event.exception)
```

### فرمت‌بندی متن

بله همه‌ی پیام‌ها را **Markdown** رندر می‌کند و پارامتر `parse_mode` نمی‌گیرد. نکته‌ی مهم:
علامت‌های `*` (بولد) و `_` (ایتالیک) باید **فاصله** قبل و بعد داشته باشند؛ ماژول `md` این کار
را انجام می‌دهد:

```python
from baleio.utils import markdown as md
await message.answer(f"{md.bold('توجه')} این یک {md.italic('نمونه')} است. {md.link('بله', 'https://bale.ai')}")
```

## دریافت آپدیت‌ها

```python
await dp.start_polling(bot)                      # async
dp.run_polling(bot)                              # blocking
await dp.start_polling(bot, drop_pending_updates=True)
```

نمونه‌ی webhook در [`examples/webhook_bot.py`](examples/webhook_bot.py).

## نمونه‌ها

- [`examples/quickstart.py`](examples/quickstart.py) — پورت quickstart رسمی aiogram
- [`examples/echo_bot.py`](examples/echo_bot.py) — اکو + کیبورد اینلاین + callback
- [`examples/fsm_form_bot.py`](examples/fsm_form_bot.py) — فرم ثبت‌نام با FSM
- [`examples/webhook_bot.py`](examples/webhook_bot.py) — دریافت آپدیت با وبهوک

## توسعه و تست

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## تفاوت‌های کلیدی با تلگرام/aiogram

بله پارامتر `parse_mode` ندارد (همیشه Markdown)، انواع آپدیت محدود به `message`,
`edited_message`, `callback_query`, `pre_checkout_query` هستند، و پرداخت فقط کیف‌پولی است.

## مشارکت

مشارکت‌ها خوش‌آمدند! لطفاً [CONTRIBUTING.md](CONTRIBUTING.md) را بخوانید و issue یا pull request باز کنید.

## مجوز

[MIT](LICENSE) © baleio contributors

> **سلب مسئولیت:** `baleio` یک پروژه‌ی مستقل و متن‌باز است و هیچ وابستگی رسمی با پیام‌رسان بله یا پروژه‌ی aiogram ندارد.
