from __future__ import annotations

import pytest

from baleio import Dispatcher, F
from baleio.filters import CallbackData, CallbackDataException
from baleio.types import CallbackQuery


class Vote(CallbackData, prefix="vote"):
    action: str
    post_id: int


class Menu(CallbackData, prefix="menu", sep="|"):
    page: int
    tab: str = "home"


def _cq_update(update_id: int, data: str) -> dict:
    return {
        "update_id": update_id,
        "callback_query": {
            "id": str(update_id),
            "from": {"id": 5, "first_name": "A"},
            "data": data,
            "message": {"message_id": 9, "chat": {"id": 5, "type": "private"}},
        },
    }


def test_pack_and_unpack_roundtrip():
    packed = Vote(action="up", post_id=7).pack()
    assert packed == "vote:up:7"
    restored = Vote.unpack(packed)
    assert restored.action == "up"
    assert restored.post_id == 7
    assert isinstance(restored.post_id, int)


def test_custom_separator():
    assert Menu(page=3, tab="x").pack() == "menu|3|x"
    assert Menu.unpack("menu|2|home").page == 2


def test_prefix_required():
    with pytest.raises(ValueError):
        class Bad(CallbackData):  # noqa: N801
            x: int


def test_length_limit():
    class Big(CallbackData, prefix="big"):
        blob: str

    with pytest.raises(CallbackDataException):
        Big(blob="x" * 100).pack()


def test_separator_in_value_raises():
    with pytest.raises(CallbackDataException):
        Vote(action="a:b", post_id=1).pack()


def test_unpack_bad_prefix():
    with pytest.raises(CallbackDataException):
        Vote.unpack("other:up:1")


@pytest.mark.asyncio
async def test_filter_injects_callback_data(bot):
    dp = Dispatcher()
    seen = []

    @dp.callback_query(Vote.filter(F.action == "up"))
    async def up(query: CallbackQuery, callback_data: Vote):
        seen.append(("up", callback_data.post_id))

    @dp.callback_query(Vote.filter())
    async def any_vote(query: CallbackQuery, callback_data: Vote):
        seen.append(("any", callback_data.action))

    await dp.feed_raw_update(bot, _cq_update(1, "vote:up:11"))     # -> up
    await dp.feed_raw_update(bot, _cq_update(2, "vote:down:22"))   # -> any_vote
    await dp.feed_raw_update(bot, _cq_update(3, "nope:x"))         # -> no match

    assert seen == [("up", 11), ("any", "down")]
