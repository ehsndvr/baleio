"""``StateFilter`` — match the current FSM state of the user."""
from __future__ import annotations

from typing import Any, Union

from ..fsm.state import State, StatesGroupMeta
from .base import BaseFilter

StateType = Union[State, str, None]


class StateFilter(BaseFilter):
    def __init__(self, *states: Union[StateType, type]) -> None:
        self.states = states

    async def __call__(self, event: Any, raw_state: Any = None, **kwargs: Any) -> bool:
        for state in self.states:
            if self._match(state, raw_state):
                return True
        return False

    @staticmethod
    def _match(expected: Any, raw_state: Any) -> bool:
        if expected is None:
            return raw_state is None
        if expected == "*":
            return True
        if isinstance(expected, State):
            return expected.state == raw_state
        if isinstance(expected, StatesGroupMeta):
            return any(s.state == raw_state for s in expected)  # type: ignore[attr-defined]
        return expected == raw_state
