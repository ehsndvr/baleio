from __future__ import annotations

import pytest

from baleio import Bot
from baleio.exceptions import BaleError
from baleio.utils import InlineKeyboardBuilder, ReplyKeyboardBuilder


def test_token_validation():
    with pytest.raises(BaleError):
        Bot("not-a-token", validate_token=True)
    # valid tokens are accepted
    b = Bot("123:abcDEF-_x", validate_token=True)
    assert b.id == 123


@pytest.mark.asyncio
async def test_send_message_returns_bound_message(bot):
    msg = await bot.send_message(10, "hello")
    assert msg.message_id == 1
    assert msg.text == "hello"
    # returned object is bound to the bot -> shortcut works
    await msg.answer("again")
    assert bot.session.methods() == ["sendMessage", "sendMessage"]


@pytest.mark.asyncio
async def test_get_chat_member_polymorphic(bot):
    bot.session.on(
        "getChatMember",
        {"status": "administrator", "user": {"id": 1, "first_name": "A"}, "can_delete_messages": True},
    )
    member = await bot.get_chat_member(10, 1)
    assert type(member).__name__ == "ChatMemberAdministrator"
    assert member.can_delete_messages is True


@pytest.mark.asyncio
async def test_download_file(bot):
    data = await bot.download_file("path/to/file.bin")
    assert data == b"filedata"


@pytest.mark.asyncio
async def test_send_copy_text(bot):
    from baleio.types import Message

    msg = Message.model_validate(
        {"message_id": 1, "chat": {"id": 5, "type": "private"}, "text": "hi"}
    ).as_(bot)
    await msg.send_copy(chat_id=99)
    assert bot.session.last()["method"] == "sendMessage"
    assert bot.session.last()["params"]["text"] == "hi"


@pytest.mark.asyncio
async def test_send_copy_photo_uses_largest_size(bot):
    from baleio.types import Message

    bot.session.on("sendPhoto", {"message_id": 2, "chat": {"id": 99, "type": "private"}})
    msg = Message.model_validate(
        {
            "message_id": 1,
            "chat": {"id": 5, "type": "private"},
            "photo": [
                {"file_id": "small", "width": 90, "height": 90},
                {"file_id": "big", "width": 900, "height": 900},
            ],
            "caption": "pic",
        }
    ).as_(bot)
    await msg.send_copy(chat_id=99)
    last = bot.session.last()
    assert last["method"] == "sendPhoto"
    assert last["params"]["photo"] == "big"
    assert last["params"]["caption"] == "pic"


@pytest.mark.asyncio
async def test_send_copy_unsupported_raises(bot):
    from baleio.types import Message

    msg = Message.model_validate(
        {
            "message_id": 1,
            "chat": {"id": 5, "type": "private"},
            "sticker": {"file_id": "s", "width": 1, "height": 1},
        }
    ).as_(bot)
    with pytest.raises(TypeError):
        await msg.send_copy(chat_id=99)


def test_markdown_module_is_exposed():
    import baleio

    assert baleio.md is baleio.markdown
    assert baleio.md.bold("x").strip() == "*x*"


def test_inline_builder_adjust():
    kb = (
        InlineKeyboardBuilder()
        .button("1", callback_data="1")
        .button("2", callback_data="2")
        .button("3", callback_data="3")
        .adjust(2, 1)
        .as_markup()
    )
    rows = kb.inline_keyboard
    assert [len(r) for r in rows] == [2, 1]


def test_reply_builder():
    kb = ReplyKeyboardBuilder().button("A").button("B").as_markup(resize_keyboard=True)
    assert kb.resize_keyboard is True
    assert kb.keyboard[0][0].text == "A"
