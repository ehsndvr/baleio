"""Filters, plus the magic ``F`` object re-exported from ``magic_filter``."""
from __future__ import annotations

from magic_filter import F, MagicFilter

from .base import BaseFilter, FilterAdapter
from .callback_data import (
    CallbackData,
    CallbackDataException,
    CallbackQueryFilter,
)
from .command import Command, CommandObject, CommandStart
from .exception import ExceptionMessageFilter, ExceptionTypeFilter
from .state import StateFilter

__all__ = [
    "F",
    "MagicFilter",
    "BaseFilter",
    "FilterAdapter",
    "Command",
    "CommandObject",
    "CommandStart",
    "StateFilter",
    "CallbackData",
    "CallbackDataException",
    "CallbackQueryFilter",
    "ExceptionTypeFilter",
    "ExceptionMessageFilter",
]
