# Dispatcher & Router

The **`Dispatcher`** is the root router and the entry point for update processing.
**`Router`** groups related handlers so you can split a large bot into modules.

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

Handlers are checked in **registration order**; the first handler whose filters all
pass runs, and propagation stops.

## Event observers

Each router exposes an observer per update type:

| Observer | Update field |
|---|---|
| `router.message` | `message` |
| `router.edited_message` | `edited_message` |
| `router.callback_query` | `callback_query` |
| `router.pre_checkout_query` | `pre_checkout_query` |
| `router.errors` | (raised exceptions, see {doc}`errors`) |

Register with the decorator form (`@router.message(...)`) or imperatively
(`router.message.register(callback, *filters)`).

## Dependency injection

A handler receives the event as its first positional argument. Any further parameters
are filled **by name** from the propagated context:

```python
from baleio import Bot
from baleio.fsm import FSMContext

@dp.message(Command("me"))
async def me(message: Message, bot: Bot, state: FSMContext):
    me = await bot.get_me()
    await message.answer(f"I am {me.first_name}")
```

Keys available for injection:

`bot`
: the `Bot` that received the update.

`state`
: an `FSMContext` scoped to the current chat/user.

`raw_state`
: the current FSM state string (or `None`).

`event_update`
: the whole `Update` object.

`event_router`
: the router that owns the matched handler.

Plus anything a filter returned as a `dict` (for example `command` from `Command`, or
`callback_data` from a `CallbackData` filter). Handlers declaring `**kwargs` receive
the entire context.

## Middlewares

Wrap handler execution with inner or outer middlewares:

```python
@dp.message.middleware               # inner: wraps the matched handler
async def timing(handler, event, data):
    import time
    start = time.perf_counter()
    result = await handler(event, data)
    print("handled in", time.perf_counter() - start, "s")
    return result

@dp.message.outer_middleware         # outer: runs before handler resolution
async def tag(handler, event, data):
    data["received_at"] = "now"
    return await handler(event, data)
```

## Receiving updates

### Long polling

```python
await dp.start_polling(bot)                          # async
dp.run_polling(bot)                                  # blocking (wraps asyncio.run)
await dp.start_polling(bot, drop_pending_updates=True)
```

### Webhook

Feed updates you receive on your own web server:

```python
from aiohttp import web
from baleio.types import Update

async def handler(request):
    await dp.feed_update(bot, Update.model_validate(await request.json()))
    return web.Response()
```
