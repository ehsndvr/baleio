from __future__ import annotations

from typing import Optional, Union

from .attachments import WebAppInfo
from .base import BaleObject


class CopyTextButton(BaleObject):
    """An inline button that copies the given text (1-256 chars)."""

    text: str


class KeyboardButton(BaleObject):
    """A button of a reply (custom) keyboard."""

    text: str
    request_contact: Optional[bool] = None
    request_location: Optional[bool] = None
    web_app: Optional[WebAppInfo] = None


class ReplyKeyboardMarkup(BaleObject):
    """A custom reply keyboard."""

    keyboard: list[list[KeyboardButton]]
    resize_keyboard: Optional[bool] = None
    one_time_keyboard: Optional[bool] = None


class ReplyKeyboardRemove(BaleObject):
    """Ask clients to remove the current custom keyboard."""

    remove_keyboard: bool = True


class InlineKeyboardButton(BaleObject):
    """A button of an inline keyboard. Use exactly one optional field."""

    text: str
    url: Optional[str] = None
    callback_data: Optional[str] = None
    web_app: Optional[WebAppInfo] = None
    copy_text: Optional[CopyTextButton] = None


class InlineKeyboardMarkup(BaleObject):
    """An inline keyboard shown right below the message it belongs to."""

    inline_keyboard: list[list[InlineKeyboardButton]]


#: Anything accepted by the ``reply_markup`` parameter.
ReplyMarkup = Union[
    "InlineKeyboardMarkup",
    "ReplyKeyboardMarkup",
    "ReplyKeyboardRemove",
]
