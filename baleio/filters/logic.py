"""Combine filters with ``&``, ``|`` and ``~``."""
from __future__ import annotations

from typing import Any, Union

from .base import BaseFilter, FilterAdapter


class _AndFilter(BaseFilter):
    def __init__(self, *targets: Any) -> None:
        self.adapters = [FilterAdapter(t) for t in targets]

    async def __call__(self, event: Any, **kwargs: Any) -> Union[bool, dict[str, Any]]:
        merged: dict[str, Any] = {}
        for adapter in self.adapters:
            result = await adapter.check(event, {**kwargs, **merged})
            if not result:
                return False
            if isinstance(result, dict):
                merged.update(result)
        return merged or True


class _OrFilter(BaseFilter):
    def __init__(self, *targets: Any) -> None:
        self.adapters = [FilterAdapter(t) for t in targets]

    async def __call__(self, event: Any, **kwargs: Any) -> Union[bool, dict[str, Any]]:
        for adapter in self.adapters:
            result = await adapter.check(event, kwargs)
            if result:
                return result if isinstance(result, dict) else True
        return False


class _InvertFilter(BaseFilter):
    def __init__(self, target: Any) -> None:
        self.adapter = FilterAdapter(target)

    async def __call__(self, event: Any, **kwargs: Any) -> bool:
        return not await self.adapter.check(event, kwargs)
