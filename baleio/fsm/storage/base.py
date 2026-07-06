"""Storage abstraction for FSM state and data."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, Union

from ..state import State


@dataclass(frozen=True)
class StorageKey:
    bot_id: int
    chat_id: int
    user_id: int

    def as_str(self) -> str:
        return f"{self.bot_id}:{self.chat_id}:{self.user_id}"


def resolve_state(state: Union[State, str, None]) -> Optional[str]:
    if state is None:
        return None
    if isinstance(state, State):
        return state.state
    return str(state)


class BaseStorage(ABC):
    @abstractmethod
    async def set_state(self, key: StorageKey, state: Union[State, str, None] = None) -> None:
        ...

    @abstractmethod
    async def get_state(self, key: StorageKey) -> Optional[str]:
        ...

    @abstractmethod
    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None:
        ...

    @abstractmethod
    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        ...

    async def update_data(self, key: StorageKey, data: dict[str, Any]) -> dict[str, Any]:
        current = await self.get_data(key)
        current.update(data)
        await self.set_data(key, current)
        return current

    async def close(self) -> None:  # pragma: no cover - overridable
        ...
