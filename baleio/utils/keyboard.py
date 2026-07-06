"""Fluent keyboard builders, mirroring aiogram's ``*Builder`` API."""
from __future__ import annotations

from typing import Any, Optional

from ..types.keyboards import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


class _BaseBuilder:
    _button_type: type

    def __init__(self, markup: Optional[list[list[Any]]] = None) -> None:
        self._rows: list[list[Any]] = list(markup or [])

    def _last_row(self) -> list[Any]:
        if not self._rows:
            self._rows.append([])
        return self._rows[-1]

    def add(self, *buttons: Any) -> "_BaseBuilder":
        """Append buttons to the current (last) row."""
        self._last_row().extend(buttons)
        return self

    def row(self, *buttons: Any) -> "_BaseBuilder":
        """Start a new row with the given buttons."""
        self._rows.append(list(buttons))
        return self

    def adjust(self, *sizes: int) -> "_BaseBuilder":
        """Reflow all buttons into rows of the given sizes (last size repeats)."""
        flat = [b for row in self._rows for b in row]
        if not sizes:
            sizes = (1,)
        new_rows: list[list[Any]] = []
        index = 0
        size_iter = list(sizes)
        pos = 0
        while index < len(flat):
            size = size_iter[min(pos, len(size_iter) - 1)]
            size = max(1, size)
            new_rows.append(flat[index : index + size])
            index += size
            pos += 1
        self._rows = new_rows
        return self

    def export(self) -> list[list[Any]]:
        return [row for row in self._rows if row]


class InlineKeyboardBuilder(_BaseBuilder):
    _button_type = InlineKeyboardButton

    def button(self, text: str, **kwargs: Any) -> "InlineKeyboardBuilder":
        self.add(InlineKeyboardButton(text=text, **kwargs))
        return self

    def as_markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=self.export())


class ReplyKeyboardBuilder(_BaseBuilder):
    _button_type = KeyboardButton

    def button(self, text: str, **kwargs: Any) -> "ReplyKeyboardBuilder":
        self.add(KeyboardButton(text=text, **kwargs))
        return self

    def as_markup(
        self,
        resize_keyboard: Optional[bool] = None,
        one_time_keyboard: Optional[bool] = None,
    ) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=self.export(),
            resize_keyboard=resize_keyboard,
            one_time_keyboard=one_time_keyboard,
        )
