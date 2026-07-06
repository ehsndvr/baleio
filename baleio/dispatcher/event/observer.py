"""Per-event registry of handlers with middleware support."""
from __future__ import annotations

from functools import partial
from typing import Any, Callable

from ...filters.base import FilterType
from .handler import HandlerObject

#: returned by :meth:`EventObserver.trigger` when no handler matched.
UNHANDLED = object()

#: middleware signature: ``async def mw(handler, event, data) -> Any``
MiddlewareType = Callable[..., Any]


class EventObserver:
    """Holds all handlers registered for a single event type."""

    def __init__(self, event_name: str) -> None:
        self.event_name = event_name
        self.handlers: list[HandlerObject] = []
        self.inner_middlewares: list[MiddlewareType] = []
        self.outer_middlewares: list[MiddlewareType] = []

    # --- registration ------------------------------------------------------
    def register(self, callback: Callable[..., Any], *filters: FilterType) -> Callable[..., Any]:
        self.handlers.append(HandlerObject(callback, list(filters)))
        return callback

    def __call__(self, *filters: FilterType) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Use as a decorator: ``@router.message(Command('start'))``."""

        def decorator(callback: Callable[..., Any]) -> Callable[..., Any]:
            self.register(callback, *filters)
            return callback

        return decorator

    def middleware(self, mw: MiddlewareType) -> MiddlewareType:
        """Register an inner middleware (wraps the matched handler)."""
        self.inner_middlewares.append(mw)
        return mw

    def outer_middleware(self, mw: MiddlewareType) -> MiddlewareType:
        """Register an outer middleware (runs before handler resolution)."""
        self.outer_middlewares.append(mw)
        return mw

    # --- execution ---------------------------------------------------------
    async def trigger(self, event: Any, data: dict[str, Any]) -> Any:
        async def resolve(ev: Any, dt: dict[str, Any]) -> Any:
            for handler in self.handlers:
                passed, extra = await handler.check(ev, dt)
                if not passed:
                    continue
                merged = {**dt, **extra, "handler": handler}
                call = self._wrap(self.inner_middlewares, handler.call)
                return await call(ev, merged)
            return UNHANDLED

        wrapped = self._wrap(self.outer_middlewares, resolve)
        return await wrapped(event, data)

    @staticmethod
    def _wrap(middlewares: list[MiddlewareType], final: Callable[..., Any]) -> Callable[..., Any]:
        handler = final
        for mw in reversed(middlewares):
            handler = partial(_apply, mw, handler)
        return handler


async def _apply(mw: MiddlewareType, nxt: Callable[..., Any], event: Any, data: dict[str, Any]) -> Any:
    return await mw(nxt, event, data)
