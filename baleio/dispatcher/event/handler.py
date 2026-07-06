"""A registered handler: a callback plus its filters."""
from __future__ import annotations

from typing import Any, Callable

from ...filters.base import FilterAdapter, FilterType, evaluate_filters
from ...utils.call import call_callback


class HandlerObject:
    def __init__(self, callback: Callable[..., Any], filters: list[FilterType]) -> None:
        self.callback = callback
        self.filters = [FilterAdapter(f) for f in filters]

    async def check(self, event: Any, data: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        return await evaluate_filters(self.filters, event, data)

    async def call(self, event: Any, data: dict[str, Any]) -> Any:
        return await call_callback(self.callback, event, data)

    def __repr__(self) -> str:
        name = getattr(self.callback, "__name__", repr(self.callback))
        return f"<HandlerObject {name} filters={len(self.filters)}>"
