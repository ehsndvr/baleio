# Filters

A filter decides whether a handler should run for a given event. baleio accepts three
kinds of filters, all interchangeable:

1. **Built-in filters** — `Command`, `CommandStart`, `StateFilter`, …
2. **Magic filter `F`** — declarative attribute matching.
3. **Plain callables** — any `(event) -> bool` (sync or async).

```python
from baleio.filters import Command, CommandStart, StateFilter, F

@dp.message(Command("help"))                          # /help
@dp.message(CommandStart())                           # /start
@dp.message(F.text == "hello")                        # magic filter
@dp.message(F.text.startswith("/"))
@dp.message(F.from_user.id == 12345)
@dp.message(lambda m: m.text and len(m.text) > 100)   # plain callable
```

## The magic filter `F`

`F` builds a predicate by describing the attribute you care about:

```python
from baleio import F

F.text == "hi"
F.text.startswith("/")
F.text.in_({"yes", "no"})
F.from_user.id == 42
F.content_type == "photo"
F.data.startswith("page:")     # on callback queries
```

## Combining filters

Filters compose with `&` (and), `|` (or), `~` (not):

```python
from baleio.filters import Command, F

@dp.message(Command("go") & (F.from_user.id == 42))
async def go(message): ...

@dp.message(F.text | F.caption)      # has text OR caption
async def any_text(message): ...

@dp.message(~F.from_user.is_bot)     # not a bot
async def humans_only(message): ...
```

## Command

`Command` matches `/command` messages and injects a `CommandObject`:

```python
from baleio.filters import Command, CommandObject

@dp.message(Command("say"))
async def say(message: Message, command: CommandObject):
    # for "/say hello world": command.command == "say", command.args == "hello world"
    await message.answer(command.args or "Say what?")
```

`CommandStart()` is shorthand for `Command("start")`.

## Filters that pass data

A filter can return a `dict` instead of `True`; those keys are merged into the handler
context and injected by name. This is how `Command` provides `command` and how
`CallbackData` provides `callback_data` (see {doc}`callback_data`).

## Writing a custom filter

Subclass `BaseFilter` and implement an async `__call__`. Declared parameters are
dependency-injected just like handlers:

```python
from baleio.filters import BaseFilter
from baleio.types import Message

class ChatType(BaseFilter):
    def __init__(self, *types: str):
        self.types = types

    async def __call__(self, message: Message) -> bool:
        return message.chat.type in self.types

@dp.message(ChatType("group", "channel"))
async def only_groups(message): ...
```

Returning a dict passes values along:

```python
class ExtractUrl(BaseFilter):
    async def __call__(self, message: Message):
        if message.text and message.text.startswith("http"):
            return {"url": message.text}
        return False

@dp.message(ExtractUrl())
async def got_url(message: Message, url: str):
    await message.answer(f"URL: {url}")
```
