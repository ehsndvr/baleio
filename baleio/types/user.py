from __future__ import annotations

from typing import Optional

from .base import BaleObject


class User(BaleObject):
    """A Bale user or bot."""

    id: int
    is_bot: Optional[bool] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None

    @property
    def full_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or ""

    @property
    def mention(self) -> str:
        name = self.full_name or (f"@{self.username}" if self.username else str(self.id))
        return name
