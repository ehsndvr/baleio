# Error handling

When processing an update raises, baleio wraps the exception in an `ErrorEvent` and
routes it to handlers registered with `@dp.errors()` — exactly like aiogram.

```python
from baleio.filters import ExceptionTypeFilter
from baleio.types import ErrorEvent

@dp.errors(ExceptionTypeFilter(ValueError))
async def on_value_error(event: ErrorEvent):
    # event.update and event.exception are available
    await event.update.message.answer("Something went wrong 😔")

@dp.errors()   # any other unhandled error
async def on_any_error(event: ErrorEvent):
    logging.exception("Unhandled", exc_info=event.exception)
```

## Behaviour

- Error handlers are matched in registration order, just like normal handlers.
- If a handler matches, the error is considered **handled** and swallowed.
- If **no** handler matches, the original exception is **re-raised**. During long
  polling it is logged and the bot keeps running; in webhook mode it propagates to your
  server so you can decide what to do.
- Error handlers themselves get dependency injection (`bot`, `event_update`,
  `exception`, …) and can use the update's shortcut methods.

## The ErrorEvent object

`event.update`
: the `Update` that was being handled (already bound to its `Bot`).

`event.exception`
: the exception instance that was raised.

## Filtering by exception

`ExceptionTypeFilter(*types)`
: match when the exception is an instance of any of the given types.

`ExceptionMessageFilter(pattern)`
: match when `str(exception)` matches a regex; the `re.Match` is injected as `match`.

```python
from baleio.filters import ExceptionMessageFilter

@dp.errors(ExceptionMessageFilter(r"rate limit"))
async def on_rate_limit(event: ErrorEvent, match):
    ...
```

## Error handlers in sub-routers

Errors propagate through the router tree, so a sub-router can define its own error
handlers, with the dispatcher's acting as a catch-all fallback.
