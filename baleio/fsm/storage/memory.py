"""In-memory FSM storage (default; not shared across processes)."""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Optional, Union

from ..state import State
from .base import BaseStorage, StorageKey, resolve_state


class MemoryStorageRecord:
    __slots__ = ("state", "data")

    def __init__(self) -> None:
        self.state: Optional[str] = None
        self.data: dict[str, Any] = {}


class MemoryStorage(BaseStorage):
    def __init__(self) -> None:
        self._store: dict[str, MemoryStorageRecord] = defaultdict(MemoryStorageRecord)

    def _record(self, key: StorageKey) -> MemoryStorageRecord:
        return self._store[key.as_str()]

    async def set_state(self, key: StorageKey, state: Union[State, str, None] = None) -> None:
        self._record(key).state = resolve_state(state)

    async def get_state(self, key: StorageKey) -> Optional[str]:
        return self._record(key).state

    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None:
        self._record(key).data = dict(data)

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        return dict(self._record(key).data)

    async def close(self) -> None:
        self._store.clear()
