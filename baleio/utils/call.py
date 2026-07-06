"""Dependency-injection helpers for calling handlers and filters.

A handler or filter receives the event as the first positional argument. Any
further parameters are filled by name from the propagated ``data`` mapping
(``bot``, ``state``, filter results, etc.). Callbacks declaring ``**kwargs``
receive the whole mapping.
"""
from __future__ import annotations

import asyncio
import inspect
from typing import Any, Callable


def _unwrap(callback: Callable[..., Any]) -> Callable[..., Any]:
    return inspect.unwrap(callback)


def accepts_var_keyword(callback: Callable[..., Any]) -> bool:
    try:
        signature = inspect.signature(_unwrap(callback))
    except (ValueError, TypeError):
        return True
    return any(
        p.kind == inspect.Parameter.VAR_KEYWORD for p in signature.parameters.values()
    )


def parameter_names(callback: Callable[..., Any]) -> list[str]:
    try:
        signature = inspect.signature(_unwrap(callback))
    except (ValueError, TypeError):
        return []
    return [
        name
        for name, p in signature.parameters.items()
        if p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)
    ]


def build_kwargs(callback: Callable[..., Any], data: dict[str, Any]) -> dict[str, Any]:
    """Pick the keys from ``data`` the callback actually declares.

    The first declared parameter receives the event positionally, so its name is
    never injected from ``data`` (otherwise an event named ``message`` in the
    data would collide with a ``message`` first parameter).
    """
    names = parameter_names(callback)
    event_param = names[0] if names else None
    if accepts_var_keyword(callback):
        return {name: value for name, value in data.items() if name != event_param}
    wanted = names[1:] if names else []
    return {name: data[name] for name in wanted if name in data}


async def call_callback(
    callback: Callable[..., Any], event: Any, data: dict[str, Any]
) -> Any:
    """Invoke ``callback(event, **injected)`` awaiting it if necessary."""
    kwargs = build_kwargs(callback, data)
    result = callback(event, **kwargs)
    if inspect.isawaitable(result):
        return await result
    return result


async def maybe_await(value: Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value


def is_async_callable(callback: Callable[..., Any]) -> bool:
    unwrapped = _unwrap(callback)
    return asyncio.iscoroutinefunction(unwrapped) or (
        callable(unwrapped) and asyncio.iscoroutinefunction(getattr(unwrapped, "__call__", None))
    )
