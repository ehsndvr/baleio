"""Shared test fixtures: an offline fake session and a bot using it."""
from __future__ import annotations

from typing import Any

import pytest

from baleio import Bot
from baleio.client.session.base import BaseSession

TEST_TOKEN = "123456:ABCDEF_test-token-value"


class FakeSession(BaseSession):
    """Records outgoing requests and returns programmable responses."""

    def __init__(self) -> None:
        super().__init__()
        self.requests: list[dict[str, Any]] = []
        self.responses: dict[str, Any] = {}

    def on(self, method: str, result: Any) -> None:
        self.responses[method] = result

    async def make_request(self, bot, method, data, timeout=None):
        params, files = self.prepare_request(data)
        self.requests.append({"method": method, "params": params, "files": files})
        if method in self.responses:
            result = self.responses[method]
            return result(params) if callable(result) else result
        # sensible defaults
        if method == "sendMessage":
            return {
                "message_id": 1,
                "chat": {"id": params.get("chat_id"), "type": "private"},
                "text": params.get("text"),
            }
        return True

    async def stream_file(self, bot, url, timeout=None):
        yield b"filedata"

    async def close(self) -> None:
        pass

    # helpers for assertions
    def last(self) -> dict[str, Any]:
        return self.requests[-1]

    def methods(self) -> list[str]:
        return [r["method"] for r in self.requests]


@pytest.fixture
def session() -> FakeSession:
    return FakeSession()


@pytest.fixture
def bot(session: FakeSession) -> Bot:
    return Bot(TEST_TOKEN, session=session)


def make_message_update(update_id: int, text: str, chat_id: int = 10, user_id: int = 10) -> dict:
    return {
        "update_id": update_id,
        "message": {
            "message_id": update_id,
            "date": 1700000000,
            "chat": {"id": chat_id, "type": "private"},
            "from": {"id": user_id, "is_bot": False, "first_name": "Tester"},
            "text": text,
        },
    }
