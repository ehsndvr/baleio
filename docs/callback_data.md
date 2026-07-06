# CallbackData factory

`CallbackData` gives you **type-safe, structured** payloads for inline buttons instead
of hand-formatting `callback_data` strings. It mirrors
`aiogram.filters.callback_data.CallbackData`.

```python
from baleio import F
from baleio.filters import CallbackData
from baleio.types import CallbackQuery
from baleio.utils import InlineKeyboardBuilder

class Vote(CallbackData, prefix="vote"):     # optional custom separator: sep="|"
    action: str
    post_id: int
```

## Packing

Build a payload and call `.pack()`:

```python
Vote(action="up", post_id=7).pack()      # -> "vote:up:7"
```

Use it as a button's `callback_data`:

```python
kb = (
    InlineKeyboardBuilder()
    .button("👍", callback_data=Vote(action="up", post_id=7).pack())
    .button("👎", callback_data=Vote(action="down", post_id=7).pack())
    .as_markup()
)
```

## Filtering & unpacking

`YourCallback.filter()` builds a filter that matches by prefix, unpacks the payload,
and injects the typed instance as `callback_data`:

```python
@dp.callback_query(Vote.filter())
async def any_vote(query: CallbackQuery, callback_data: Vote):
    await query.answer(f"{callback_data.action} on post {callback_data.post_id}")
```

Combine with the magic filter to route on a specific field:

```python
@dp.callback_query(Vote.filter(F.action == "up"))
async def upvote(query: CallbackQuery, callback_data: Vote):
    await query.answer("liked!")
```

Fields are coerced back to their declared types on unpack — `callback_data.post_id` is
an `int`, not a string.

## Rules & limits

- Every subclass **must** declare a `prefix`.
- The separator (`:` by default) may not appear in the prefix or in any field value.
- Bale limits `callback_data` to **64 bytes**; `.pack()` raises `CallbackDataException`
  if the result is longer.
- Optional fields serialize to an empty segment and unpack back to `None`.

```python
from baleio.filters import CallbackDataException

class Menu(CallbackData, prefix="menu", sep="|"):
    page: int
    tab: str = "home"

Menu(page=2, tab="settings").pack()      # -> "menu|2|settings"
Menu.unpack("menu|2|home")               # -> Menu(page=2, tab="home")
```
