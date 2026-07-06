"""Filter protocol and the adapter that normalises every filter kind."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Union

from magic_filter import MagicFilter

from ..utils.call import call_callback, maybe_await


class BaseFilter(ABC):
    """Subclass and implement :meth:`__call__` to build a reusable filter.

    A filter returns a falsy value to reject the event, or ``True`` / a ``dict``
    to accept it. A returned dict is merged into the handler ``data`` so filters
    can pass extracted values (e.g. command arguments) to handlers.
    """

    @abstractmethod
    async def __call__(self, event: Any, **kwargs: Any) -> Union[bool, dict[str, Any]]:
        ...

    def __and__(self, other: Any) -> "BaseFilter":
        from .logic import _AndFilter

        return _AndFilter(self, other)

    def __or__(self, other: Any) -> "BaseFilter":
        from .logic import _OrFilter

        return _OrFilter(self, other)

    def __invert__(self) -> "BaseFilter":
        from .logic import _InvertFilter

        return _InvertFilter(self)


FilterType = Union[BaseFilter, MagicFilter, Callable[..., Any]]


class FilterAdapter:
    """Wraps any supported filter into a uniform ``check(event, data)`` call."""

    def __init__(self, filter_: FilterType) -> None:
        self.filter = self._normalize(filter_)

    @staticmethod
    def _normalize(filter_: Any) -> Any:
        # Allow passing a State / StatesGroup directly as a filter, e.g.
        # ``@router.message(Form.name)`` — wrap it in a StateFilter.
        from ..fsm.state import State, StatesGroupMeta

        if isinstance(filter_, State) or isinstance(filter_, StatesGroupMeta):
            from .state import StateFilter

            return StateFilter(filter_)
        return filter_

    async def check(self, event: Any, data: dict[str, Any]) -> Union[bool, dict[str, Any]]:
        f = self.filter
        if isinstance(f, MagicFilter):
            return bool(f.resolve(event))
        # BaseFilter instances and plain callables both go through dependency
        # injection so their declared parameters (bot, state, ...) get filled.
        return await call_callback(f, event, data)


async def evaluate_filters(
    filters: list[FilterAdapter], event: Any, data: dict[str, Any]
) -> tuple[bool, dict[str, Any]]:
    """Return ``(passed, extra_data)`` after running every filter in order."""
    extra: dict[str, Any] = {}
    for adapter in filters:
        result = await adapter.check(event, {**data, **extra})
        if not result:
            return False, {}
        if isinstance(result, dict):
            extra.update(result)
    return True, extra
