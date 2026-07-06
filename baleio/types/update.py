from __future__ import annotations

from typing import Optional

from ..enums import UpdateType
from .base import BaleObject
from .callback import CallbackQuery
from .message import Message
from .payments import PreCheckoutQuery


class Update(BaleObject):
    """An incoming update. At most one optional field is set."""

    update_id: int
    message: Optional[Message] = None
    edited_message: Optional[Message] = None
    callback_query: Optional[CallbackQuery] = None
    pre_checkout_query: Optional[PreCheckoutQuery] = None

    @property
    def event_type(self) -> str:
        """Name of the populated update field."""
        for name in UpdateType:
            if getattr(self, name.value, None) is not None:
                return name.value
        return "unknown"

    @property
    def event(self) -> Optional[BaleObject]:
        """The populated update object itself."""
        value = getattr(self, self.event_type, None)
        return value
