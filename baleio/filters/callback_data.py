"""``CallbackData`` factory — structured, type-safe callback payloads.

Mirrors ``aiogram.filters.callback_data``::

    class Vote(CallbackData, prefix="vote"):
        action: str
        post_id: int

    button = InlineKeyboardButton(text="👍", callback_data=Vote(action="up", post_id=7).pack())
    # -> callback_data == "vote:up:7"

    @router.callback_query(Vote.filter(F.action == "up"))
    async def on_up(query: CallbackQuery, callback_data: Vote):
        await query.answer(f"post {callback_data.post_id}")
"""
from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import Any, ClassVar, Optional, Union
from uuid import UUID

from magic_filter import MagicFilter
from pydantic import BaseModel, ValidationError

from ..exceptions import BaleError
from ..types.callback import CallbackQuery
from .base import BaseFilter

#: Bale limits ``InlineKeyboardButton.callback_data`` to 1–64 bytes.
MAX_CALLBACK_DATA_LENGTH = 64
DEFAULT_SEPARATOR = ":"


class CallbackDataException(BaleError):
    """Raised when a callback payload cannot be packed or unpacked."""


class CallbackData(BaseModel):
    """Base class for structured callback payloads.

    Subclass it with a ``prefix`` (and optionally a ``sep``)::

        class Menu(CallbackData, prefix="menu", sep="|"):
            page: int
    """

    __separator__: ClassVar[str] = DEFAULT_SEPARATOR
    __prefix__: ClassVar[str] = ""

    def __init_subclass__(
        cls, *, prefix: Optional[str] = None, sep: str = DEFAULT_SEPARATOR, **kwargs: Any
    ) -> None:
        super().__init_subclass__(**kwargs)
        if prefix is None:
            raise ValueError(
                f"CallbackData subclass {cls.__name__!r} must define a `prefix`, "
                f"e.g. `class {cls.__name__}(CallbackData, prefix='...')`."
            )
        if sep in prefix:
            raise ValueError(
                f"Separator {sep!r} may not appear in prefix {prefix!r}."
            )
        cls.__prefix__ = prefix
        cls.__separator__ = sep

    # --- packing -----------------------------------------------------------
    def pack(self) -> str:
        parts = [self.__prefix__]
        for name in type(self).model_fields:
            encoded = self._encode(getattr(self, name))
            if self.__separator__ in encoded:
                raise CallbackDataException(
                    f"Separator {self.__separator__!r} found in value of field "
                    f"{name!r}: {encoded!r}. Choose a different `sep`."
                )
            parts.append(encoded)
        value = self.__separator__.join(parts)
        length = len(value.encode("utf-8"))
        if length > MAX_CALLBACK_DATA_LENGTH:
            raise CallbackDataException(
                f"Packed callback data is {length} bytes, exceeding the "
                f"{MAX_CALLBACK_DATA_LENGTH}-byte limit: {value!r}"
            )
        return value

    @classmethod
    def unpack(cls, value: str) -> "CallbackData":
        field_names = list(cls.model_fields.keys())
        prefix, *parts = value.split(cls.__separator__, maxsplit=len(field_names))
        if prefix != cls.__prefix__:
            raise CallbackDataException(
                f"Bad prefix: expected {cls.__prefix__!r}, got {prefix!r}."
            )
        if len(parts) != len(field_names):
            raise CallbackDataException(
                f"Expected {len(field_names)} values for {cls.__name__}, got {len(parts)}."
            )
        payload = {
            name: (None if raw == "" else raw)
            for name, raw in zip(field_names, parts)
        }
        return cls(**payload)

    @classmethod
    def filter(cls, rule: Optional[Union[MagicFilter, Any]] = None) -> "CallbackQueryFilter":
        return CallbackQueryFilter(callback_data=cls, rule=rule)

    @staticmethod
    def _encode(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, Enum):
            value = value.value
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, (UUID, Decimal)):
            return str(value)
        return str(value)


class CallbackQueryFilter(BaseFilter):
    """Filter produced by :meth:`CallbackData.filter`."""

    def __init__(
        self,
        callback_data: type[CallbackData],
        rule: Optional[Union[MagicFilter, Any]] = None,
    ) -> None:
        self.callback_data = callback_data
        self.rule = rule

    async def __call__(self, query: Any, **kwargs: Any) -> Union[bool, dict[str, Any]]:
        if not isinstance(query, CallbackQuery) or not query.data:
            return False
        try:
            data = self.callback_data.unpack(query.data)
        except (CallbackDataException, ValidationError, ValueError, TypeError):
            return False
        if self.rule is not None and not self._check_rule(data):
            return False
        return {"callback_data": data}

    def _check_rule(self, data: CallbackData) -> bool:
        if isinstance(self.rule, MagicFilter):
            return bool(self.rule.resolve(data))
        if callable(self.rule):
            return bool(self.rule(data))
        return bool(self.rule)
