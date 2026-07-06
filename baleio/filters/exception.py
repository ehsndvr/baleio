"""Filters for ``@dp.errors()`` handlers."""
from __future__ import annotations

import re
from typing import Any, Pattern, Union

from .base import BaseFilter


class ExceptionTypeFilter(BaseFilter):
    """Match an :class:`~baleio.types.ErrorEvent` by its exception type.

        @dp.errors(ExceptionTypeFilter(ValueError, KeyError))
        async def on_value_error(event: ErrorEvent): ...
    """

    def __init__(self, *exceptions: type[Exception]) -> None:
        if not exceptions:
            raise ValueError("ExceptionTypeFilter needs at least one exception type")
        self.exceptions = exceptions

    async def __call__(self, event: Any, **kwargs: Any) -> bool:
        exception = getattr(event, "exception", None)
        return isinstance(exception, self.exceptions)


class ExceptionMessageFilter(BaseFilter):
    """Match an error event when ``str(exception)`` matches a regex pattern."""

    def __init__(self, pattern: Union[str, Pattern]) -> None:
        self.pattern = re.compile(pattern) if isinstance(pattern, str) else pattern

    async def __call__(self, event: Any, **kwargs: Any) -> Union[bool, dict[str, Any]]:
        exception = getattr(event, "exception", None)
        if exception is None:
            return False
        match = self.pattern.match(str(exception))
        if match is None:
            return False
        return {"match": match}
