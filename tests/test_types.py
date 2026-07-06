from __future__ import annotations

from baleio.enums import ContentType
from baleio.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    parse_chat_member,
)


def test_update_parsing_and_from_alias():
    u = Update.model_validate(
        {
            "update_id": 7,
            "message": {
                "message_id": 3,
                "chat": {"id": 1, "type": "private"},
                "from": {"id": 42, "is_bot": False, "first_name": "Sara"},
                "text": "/help me",
            },
        }
    )
    assert u.event_type == "message"
    assert u.message.from_user.id == 42
    assert u.message.from_user.full_name == "Sara"
    assert u.message.content_type == ContentType.TEXT
    assert u.message.get_args() == "me"


def test_callback_query_from_alias():
    cq = CallbackQuery.model_validate(
        {"id": "9", "from": {"id": 5, "first_name": "X"}, "data": "yes"}
    )
    assert cq.from_user.id == 5
    assert cq.data == "yes"


def test_chat_member_polymorphism():
    owner = parse_chat_member({"status": "creator", "user": {"id": 1, "first_name": "A"}})
    admin = parse_chat_member(
        {"status": "administrator", "user": {"id": 2, "first_name": "B"}, "can_delete_messages": True}
    )
    assert type(owner).__name__ == "ChatMemberOwner"
    assert type(admin).__name__ == "ChatMemberAdministrator"
    assert admin.can_delete_messages is True


def test_keyboard_dump_excludes_none():
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Go", url="https://ble.ir")]]
    )
    dumped = kb.model_dump_api()
    assert dumped == {"inline_keyboard": [[{"text": "Go", "url": "https://ble.ir"}]]}


def test_message_entity_utf16_extract():
    from baleio.types import MessageEntity

    text = "hi @user"
    ent = MessageEntity(type="mention", offset=3, length=5)
    assert ent.extract_from(text) == "@user"
