"""Default bot-wide properties.

Bale renders every message as Markdown and (unlike Telegram) does not accept a
``parse_mode`` request parameter, so these defaults are intentionally small.
They exist for API familiarity and future expansion.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class DefaultBotProperties:
    #: Kept for parity with aiogram; Bale ignores an explicit parse mode.
    parse_mode: Optional[str] = None
    #: Default value for ``reply_to_message_id`` protection, unused for now.
    protect_content: Optional[bool] = None
