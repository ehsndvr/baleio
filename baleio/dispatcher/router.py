"""Router — groups handlers and can be nested inside other routers."""
from __future__ import annotations

from typing import Any, Optional

from ..enums import UpdateType
from .event.observer import UNHANDLED, EventObserver

#: the update fields a router can observe
OBSERVED_EVENTS = (
    UpdateType.MESSAGE.value,
    UpdateType.EDITED_MESSAGE.value,
    UpdateType.CALLBACK_QUERY.value,
    UpdateType.PRE_CHECKOUT_QUERY.value,
)


class Router:
    """A collection of event observers and child routers."""

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name or hex(id(self))
        self.parent_router: Optional["Router"] = None
        self.sub_routers: list["Router"] = []

        self.message = EventObserver(UpdateType.MESSAGE.value)
        self.edited_message = EventObserver(UpdateType.EDITED_MESSAGE.value)
        self.callback_query = EventObserver(UpdateType.CALLBACK_QUERY.value)
        self.pre_checkout_query = EventObserver(UpdateType.PRE_CHECKOUT_QUERY.value)
        #: error handlers, triggered when handling an update raises
        self.errors = EventObserver("error")
        self.error = self.errors  # aiogram-style alias

        self.observers: dict[str, EventObserver] = {
            UpdateType.MESSAGE.value: self.message,
            UpdateType.EDITED_MESSAGE.value: self.edited_message,
            UpdateType.CALLBACK_QUERY.value: self.callback_query,
            UpdateType.PRE_CHECKOUT_QUERY.value: self.pre_checkout_query,
            "error": self.errors,
        }

    # --- nesting -----------------------------------------------------------
    def include_router(self, router: "Router") -> "Router":
        if not isinstance(router, Router):
            raise TypeError(f"include_router expects a Router, got {type(router)!r}")
        if router is self:
            raise RuntimeError("A router cannot include itself")
        if router.parent_router is not None:
            raise RuntimeError(f"Router {router.name!r} is already attached")
        router.parent_router = self
        self.sub_routers.append(router)
        return router

    def include_routers(self, *routers: "Router") -> None:
        for router in routers:
            self.include_router(router)

    # --- propagation -------------------------------------------------------
    async def propagate_event(self, event_type: str, event: Any, data: dict[str, Any]) -> Any:
        observer = self.observers.get(event_type)
        if observer is not None:
            result = await observer.trigger(event, {**data, "event_router": self})
            if result is not UNHANDLED:
                return result
        for router in self.sub_routers:
            result = await router.propagate_event(event_type, event, data)
            if result is not UNHANDLED:
                return result
        return UNHANDLED

    def __repr__(self) -> str:
        return f"<Router {self.name!r}>"
