from __future__ import annotations

import pytest

from baleio import Dispatcher, Router
from baleio.filters import Command, ExceptionMessageFilter, ExceptionTypeFilter
from baleio.types import ErrorEvent, Message

from conftest import make_message_update


@pytest.mark.asyncio
async def test_error_handler_catches_and_swallows(bot):
    dp = Dispatcher()
    seen = []

    @dp.message(Command("boom"))
    async def boom(m: Message):
        raise ValueError("kaboom")

    @dp.errors(ExceptionTypeFilter(ValueError))
    async def on_error(event: ErrorEvent, exception):
        seen.append((type(event.exception).__name__, str(exception)))

    # does not raise
    await dp.feed_raw_update(bot, make_message_update(1, "/boom"))
    assert seen == [("ValueError", "kaboom")]


@pytest.mark.asyncio
async def test_unmatched_error_is_reraised(bot):
    dp = Dispatcher()

    @dp.message(Command("boom"))
    async def boom(m: Message):
        raise KeyError("missing")

    @dp.errors(ExceptionTypeFilter(ValueError))  # does not match KeyError
    async def on_value(event: ErrorEvent):
        ...

    with pytest.raises(KeyError):
        await dp.feed_raw_update(bot, make_message_update(1, "/boom"))


@pytest.mark.asyncio
async def test_error_handler_can_use_update_shortcuts(bot):
    dp = Dispatcher()

    @dp.message(Command("boom"))
    async def boom(m: Message):
        raise RuntimeError("oops")

    @dp.errors()
    async def on_error(event: ErrorEvent):
        await event.update.message.answer("handled")

    await dp.feed_raw_update(bot, make_message_update(1, "/boom"))
    assert bot.session.last()["method"] == "sendMessage"
    assert bot.session.last()["params"]["text"] == "handled"


@pytest.mark.asyncio
async def test_exception_message_filter(bot):
    dp = Dispatcher()
    hits = []

    @dp.message(Command("boom"))
    async def boom(m: Message):
        raise ValueError("rate limit exceeded")

    @dp.errors(ExceptionMessageFilter(r"rate limit"))
    async def on_rate(event: ErrorEvent, match):
        hits.append(match.group(0))

    await dp.feed_raw_update(bot, make_message_update(1, "/boom"))
    assert hits == ["rate limit"]


@pytest.mark.asyncio
async def test_error_handler_in_subrouter(bot):
    dp = Dispatcher()
    sub = Router(name="sub")
    seen = []

    @sub.message(Command("x"))
    async def x(m: Message):
        raise ValueError("from sub")

    @dp.errors()
    async def root_errors(event: ErrorEvent):
        seen.append(str(event.exception))

    dp.include_router(sub)
    await dp.feed_raw_update(bot, make_message_update(1, "/x"))
    assert seen == ["from sub"]
