"""String enums used across the Bale API.

All of them subclass ``str`` so they can be passed directly to the API and
compared transparently to plain strings.
"""
from __future__ import annotations

from enum import Enum


class _StrEnum(str, Enum):
    def __str__(self) -> str:  # pragma: no cover - trivial
        return str(self.value)

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"{type(self).__name__}.{self.name}"


class ChatType(_StrEnum):
    """Type of a chat."""

    PRIVATE = "private"
    GROUP = "group"
    CHANNEL = "channel"


class ChatAction(_StrEnum):
    """Actions shown in the chat while the bot is busy."""

    TYPING = "typing"
    UPLOAD_PHOTO = "upload_photo"
    RECORD_VIDEO = "record_video"
    UPLOAD_VIDEO = "upload_video"
    RECORD_VOICE = "record_voice"
    UPLOAD_VOICE = "upload_voice"
    CHOOSE_STICKER = "choose_sticker"


class ChatMemberStatus(_StrEnum):
    """Membership status inside a chat."""

    CREATOR = "creator"
    ADMINISTRATOR = "administrator"
    MEMBER = "member"
    RESTRICTED = "restricted"


class MessageEntityType(_StrEnum):
    """Kinds of entities found in message text."""

    MENTION = "mention"
    BOT_COMMAND = "bot_command"


class ParseMode(_StrEnum):
    """Text formatting mode. Bale currently formats everything as Markdown."""

    MARKDOWN = "Markdown"
    HTML = "HTML"


class StickerType(_StrEnum):
    REGULAR = "regular"
    MASK = "mask"


class InputMediaType(_StrEnum):
    PHOTO = "photo"
    VIDEO = "video"
    ANIMATION = "animation"
    AUDIO = "audio"
    DOCUMENT = "document"


class TransactionStatus(_StrEnum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REJECTED = "rejected"


class Currency(_StrEnum):
    IRR = "IRR"


class UpdateType(_StrEnum):
    """Names of the update fields the dispatcher can route on."""

    MESSAGE = "message"
    EDITED_MESSAGE = "edited_message"
    CALLBACK_QUERY = "callback_query"
    PRE_CHECKOUT_QUERY = "pre_checkout_query"


class ContentType(_StrEnum):
    """Type of the content carried by a message."""

    TEXT = "text"
    ANIMATION = "animation"
    AUDIO = "audio"
    DOCUMENT = "document"
    PHOTO = "photo"
    STICKER = "sticker"
    VIDEO = "video"
    VOICE = "voice"
    CONTACT = "contact"
    LOCATION = "location"
    INVOICE = "invoice"
    SUCCESSFUL_PAYMENT = "successful_payment"
    NEW_CHAT_MEMBERS = "new_chat_members"
    LEFT_CHAT_MEMBER = "left_chat_member"
    WEB_APP_DATA = "web_app_data"
    UNKNOWN = "unknown"


__all__ = [
    "ChatType",
    "ChatAction",
    "ChatMemberStatus",
    "MessageEntityType",
    "ParseMode",
    "StickerType",
    "InputMediaType",
    "TransactionStatus",
    "Currency",
    "UpdateType",
    "ContentType",
]
