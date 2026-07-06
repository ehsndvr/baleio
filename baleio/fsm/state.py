"""Finite-state-machine states, aiogram-style.

Example::

    class Registration(StatesGroup):
        name = State()
        age = State()
"""
from __future__ import annotations

from typing import Any, Optional


class State:
    """A single state. Belongs to a :class:`StatesGroup`."""

    def __init__(self, state: Optional[str] = None) -> None:
        self._state = state
        self._group_name: Optional[str] = None
        self._name: Optional[str] = None

    def __set_name__(self, owner: type, name: str) -> None:
        self._name = name

    def _set_parent(self, group_name: str) -> None:
        self._group_name = group_name

    @property
    def state(self) -> Optional[str]:
        if self._state == "*":
            return "*"
        if self._state is not None:
            return self._state
        if self._name is None:
            return None
        if self._group_name:
            return f"{self._group_name}:{self._name}"
        return self._name

    def __str__(self) -> str:
        return f"State({self.state!r})"

    __repr__ = __str__

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, State):
            return self.state == other.state
        return self.state == other

    def __hash__(self) -> int:
        return hash(self.state)


class StatesGroupMeta(type):
    def __new__(mcs, name: str, bases: tuple[type, ...], namespace: dict[str, Any]):
        cls = super().__new__(mcs, name, bases, namespace)
        cls.__full_group_name__ = name  # type: ignore[attr-defined]
        states: list[State] = []
        for value in namespace.values():
            if isinstance(value, State):
                value._set_parent(name)
                states.append(value)
        cls.__states__ = tuple(states)  # type: ignore[attr-defined]
        return cls

    def __contains__(cls, item: Any) -> bool:
        if isinstance(item, State):
            return item in cls.__states__  # type: ignore[attr-defined]
        return any(s.state == item for s in cls.__states__)  # type: ignore[attr-defined]

    def __iter__(cls):
        return iter(cls.__states__)  # type: ignore[attr-defined]


class StatesGroup(metaclass=StatesGroupMeta):
    """Base class for a named group of :class:`State` objects."""


#: Special state matching every FSM state.
default_state = State(state=None)
any_state = State(state="*")
