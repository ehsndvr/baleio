"""All Bale API object types."""
from __future__ import annotations

from .attachments import (
    Contact,
    Invoice,
    Location,
    MessageEntity,
    MessageId,
    WebAppData,
    WebAppInfo,
)
from .base import BaleObject, MutableBaleObject, bot_context
from .callback import CallbackQuery
from .chat import (
    AnyChatMember,
    Chat,
    ChatFullInfo,
    ChatMember,
    ChatMemberAdministrator,
    ChatMemberMember,
    ChatMemberOwner,
    ChatMemberRestricted,
    parse_chat_member,
)
from .error import ErrorEvent
from .input_file import BufferedInputFile, FSInputFile, InputFile, URLInputFile
from .input_media import (
    InputMedia,
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    InputSticker,
)
from .keyboards import (
    CopyTextButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    ReplyMarkup,
)
from .media import (
    Animation,
    Audio,
    ChatPhoto,
    Document,
    File,
    PhotoSize,
    Sticker,
    StickerSet,
    Video,
    Voice,
)
from .message import Message
from .misc import ResponseParameters, WebhookInfo
from .payments import (
    LabeledPrice,
    PreCheckoutQuery,
    SuccessfulPayment,
    Transaction,
)
from .update import Update
from .user import User

# Resolve forward references now that every model is importable.
_rebuild_ns = {
    "InlineKeyboardMarkup": InlineKeyboardMarkup,
    "ReplyKeyboardMarkup": ReplyKeyboardMarkup,
    "ReplyKeyboardRemove": ReplyKeyboardRemove,
    "Message": Message,
    "CallbackQuery": CallbackQuery,
    "User": User,
    "Chat": Chat,
}
for _model in (Message, CallbackQuery, Update, Chat, ChatFullInfo, PreCheckoutQuery):
    _model.model_rebuild(_types_namespace=_rebuild_ns)

ErrorEvent.model_rebuild(_types_namespace={"Update": Update, "Exception": Exception})

__all__ = [
    "BaleObject",
    "MutableBaleObject",
    "bot_context",
    "Update",
    "User",
    "Chat",
    "ChatFullInfo",
    "Message",
    "MessageId",
    "MessageEntity",
    "CallbackQuery",
    "ErrorEvent",
    "Contact",
    "Location",
    "Invoice",
    "WebAppData",
    "WebAppInfo",
    "PhotoSize",
    "Animation",
    "Audio",
    "Document",
    "Video",
    "Voice",
    "Sticker",
    "StickerSet",
    "File",
    "ChatPhoto",
    "ChatMember",
    "ChatMemberOwner",
    "ChatMemberAdministrator",
    "ChatMemberMember",
    "ChatMemberRestricted",
    "AnyChatMember",
    "parse_chat_member",
    "ReplyKeyboardMarkup",
    "KeyboardButton",
    "InlineKeyboardMarkup",
    "InlineKeyboardButton",
    "ReplyKeyboardRemove",
    "CopyTextButton",
    "ReplyMarkup",
    "InputFile",
    "BufferedInputFile",
    "FSInputFile",
    "URLInputFile",
    "InputMedia",
    "InputMediaPhoto",
    "InputMediaVideo",
    "InputMediaAnimation",
    "InputMediaAudio",
    "InputMediaDocument",
    "InputSticker",
    "LabeledPrice",
    "PreCheckoutQuery",
    "SuccessfulPayment",
    "Transaction",
    "WebhookInfo",
    "ResponseParameters",
]
