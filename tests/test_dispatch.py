from __future__ import annotations

import pytest

from baleio import Dispatcher, F
from baleio.filters import Command, StateFilter
from baleio.fsm import State, StatesGroup
from baleio.types import CallbackQuery, Message

from conftest import make_message_update


class Reg(StatesGroup):
    name = State()


@pytest.mark.asyncio
async def test_command_and_fsm_flow(bot):
    dp = Dispatcher()
    seen = []

    @dp.message(Command("start"))
    async def start(m: Message, state):
        seen.append(("start", m.get_args()))
        await state.set_state(Reg.name)
        await m.answer("name?")

    @dp.message(StateFilter(Reg.name))
    async def name(m: Message, state):
        await state.update_data(name=m.text)
        data = await state.get_data()
        seen.append(("name", data["name"]))
        await state.clear()

    await dp.feed_raw_update(bot, make_message_update(1, "/start x"))
    await dp.feed_raw_update(bot, make_message_update(2, "Ali"))

    assert seen == [("start", "x"), ("name", "Ali")]
    assert bot.session.methods() == ["sendMessage"]


@pytest.mark.asyncio
async def test_magic_filter(bot):
    dp = Dispatcher()
    hits = []

    @dp.message(F.text == "ping")
    async def ping(m: Message):
        hits.append(m.text)
        await m.answer("pong")

    await dp.feed_raw_update(bot, make_message_update(1, "ping"))
    await dp.feed_raw_update(bot, make_message_update(2, "nope"))
    assert hits == ["ping"]


@pytest.mark.asyncio
async def test_callback_query(bot):
    dp = Dispatcher()
    hits = []

    @dp.callback_query(F.data == "ok")
    async def cb(c: CallbackQuery):
        hits.append(c.data)
        await c.answer("done")

    update = {
        "update_id": 1,
        "callback_query": {
            "id": "1",
            "from": {"id": 3, "first_name": "Z"},
            "data": "ok",
            "message": {"message_id": 5, "chat": {"id": 3, "type": "private"}},
        },
    }
    await dp.feed_raw_update(bot, update)
    assert hits == ["ok"]
    assert bot.session.methods() == ["answerCallbackQuery"]


@pytest.mark.asyncio
async def test_router_nesting(bot):
    from baleio import Router

    dp = Dispatcher()
    sub = Router(name="sub")
    order = []

    @sub.message(Command("sub"))
    async def sub_handler(m: Message):
        order.append("sub")

    @dp.message(Command("root"))
    async def root_handler(m: Message):
        order.append("root")

    dp.include_router(sub)
    await dp.feed_raw_update(bot, make_message_update(1, "/sub"))
    await dp.feed_raw_update(bot, make_message_update(2, "/root"))
    assert order == ["sub", "root"]


@pytest.mark.asyncio
async def test_filter_combinators(bot):
    dp = Dispatcher()
    hits = []

    @dp.message(Command("go") & (F.from_user.id == 10))
    async def go(m: Message):
        hits.append(m.message_id)

    await dp.feed_raw_update(bot, make_message_update(1, "/go", user_id=10))
    await dp.feed_raw_update(bot, make_message_update(2, "/go", user_id=999))
    assert hits == [1]


@pytest.mark.asyncio
async def test_feed_update_propagates_handler_errors(bot):
    dp = Dispatcher()

    @dp.message(Command("boom"))
    async def boom(m: Message):
        raise ValueError("kaboom")

    with pytest.raises(ValueError, match="kaboom"):
        await dp.feed_raw_update(bot, make_message_update(1, "/boom"))


@pytest.mark.asyncio
async def test_middleware(bot):
    dp = Dispatcher()
    trail = []

    @dp.message.middleware
    async def mw(handler, event, data):
        trail.append("before")
        result = await handler(event, data)
        trail.append("after")
        return result

    @dp.message(Command("x"))
    async def handler(m: Message):
        trail.append("handler")

    await dp.feed_raw_update(bot, make_message_update(1, "/x"))
    assert trail == ["before", "handler", "after"]
