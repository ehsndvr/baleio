from __future__ import annotations

from typing import Optional

from .base import BaleObject


class WebhookInfo(BaleObject):
    """Current webhook status."""

    url: Optional[str] = None


class ResponseParameters(BaleObject):
    """Extra information attached to a failed request."""

    retry_after: Optional[int] = None
    migrate_to_chat_id: Optional[int] = None
