from __future__ import annotations

from typing import Optional

from .base import BaleObject


class Contact(BaleObject):
    phone_number: str
    first_name: str
    last_name: Optional[str] = None
    user_id: Optional[int] = None


class Location(BaleObject):
    longitude: float
    latitude: float


class Invoice(BaleObject):
    title: str
    description: str
    total_amount: int


class WebAppData(BaleObject):
    """Data sent to the bot from a mini app."""

    data: str


class WebAppInfo(BaleObject):
    """Describes a mini app opened by a button."""

    url: str


class MessageId(BaleObject):
    message_id: int


class MessageEntity(BaleObject):
    """A special part of message text (mention, bot command, ...)."""

    type: str
    offset: int
    length: int

    def extract_from(self, text: str) -> str:
        """Return the substring of ``text`` this entity covers (UTF-16 aware)."""
        encoded = text.encode("utf-16-le")
        chunk = encoded[self.offset * 2 : (self.offset + self.length) * 2]
        return chunk.decode("utf-16-le")
