# Keyboards

baleio provides builders for both inline and reply keyboards, plus the raw markup types.

## Inline keyboards

```python
from baleio.utils import InlineKeyboardBuilder

kb = (
    InlineKeyboardBuilder()
    .button("Yes", callback_data="yes")
    .button("No", callback_data="no")
    .adjust(2)                       # 2 buttons per row
    .as_markup()
)
await message.answer("Agree?", reply_markup=kb)
```

Handle the click and **always** answer the callback query to release the button:

```python
from baleio import F

@dp.callback_query(F.data == "yes")
async def yes(cb):
    await cb.answer("Great!", show_alert=True)
    await cb.message.edit_text("You chose: Yes")
```

Inline buttons support `url`, `callback_data`, `web_app`, and `copy_text`:

```python
from baleio.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, CopyTextButton

markup = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text="Open site", url="https://bale.ai"),
    InlineKeyboardButton(text="Mini app", web_app=WebAppInfo(url="https://example.com")),
    InlineKeyboardButton(text="Copy code", copy_text=CopyTextButton(text="PROMO2026")),
]])
```

## Reply keyboards

```python
from baleio.utils import ReplyKeyboardBuilder

kb = (
    ReplyKeyboardBuilder()
    .button("Share contact", request_contact=True)
    .button("Share location", request_location=True)
    .adjust(1)
    .as_markup(resize_keyboard=True, one_time_keyboard=True)
)
await message.answer("Choose:", reply_markup=kb)
```

Remove a custom keyboard:

```python
from baleio.types import ReplyKeyboardRemove

await message.answer("Done.", reply_markup=ReplyKeyboardRemove())
```

## Builder helpers

`.button(text, **kwargs)`
: add a single button.

`.row(*buttons)`
: add a full row of pre-built buttons.

`.adjust(*sizes)`
: re-flow buttons into rows of the given sizes (e.g. `.adjust(2, 1)`).

`.as_markup(**kwargs)`
: finalize into an `InlineKeyboardMarkup` / `ReplyKeyboardMarkup`.
