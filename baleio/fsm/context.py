"""FSMContext — the per-user handle handlers use to read/write state."""
from __future__ import annotations

from typing import Any, Optional, Union

from .state import State
from .storage.base import BaseStorage, StorageKey


class FSMContext:
    def __init__(self, storage: BaseStorage, key: StorageKey) -> None:
        self.storage = storage
        self.key = key

    async def set_state(self, state: Union[State, str, None] = None) -> None:
        await self.storage.set_state(self.key, state)

    async def get_state(self) -> Optional[str]:
        return await self.storage.get_state(self.key)

    async def set_data(self, data: dict[str, Any]) -> None:
        await self.storage.set_data(self.key, data)

    async def get_data(self) -> dict[str, Any]:
        return await self.storage.get_data(self.key)

    async def update_data(self, data: Optional[dict[str, Any]] = None, **kwargs: Any) -> dict[str, Any]:
        payload = {**(data or {}), **kwargs}
        return await self.storage.update_data(self.key, payload)

    async def clear(self) -> None:
        await self.set_state(None)
        await self.set_data({})
