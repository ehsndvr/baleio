from __future__ import annotations

from baleio.client.session.base import BaseSession
from baleio.types import (
    BufferedInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    LabeledPrice,
)


class _S(BaseSession):
    async def make_request(self, *a, **k):
        ...

    async def stream_file(self, *a, **k):
        yield b""

    async def close(self):
        ...


def test_json_path_no_files():
    s = _S()
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="x", callback_data="y")]]
    )
    params, files = s.prepare_request({"chat_id": 1, "text": "hi", "reply_markup": kb, "skip": None})
    assert files == {}
    assert params["reply_markup"] == {"inline_keyboard": [[{"text": "x", "callback_data": "y"}]]}
    assert "skip" not in params


def test_prices_serialized_as_list_of_dicts():
    s = _S()
    params, files = s.prepare_request({"prices": [LabeledPrice(label="a", amount=1000)]})
    assert params["prices"] == [{"label": "a", "amount": 1000}]


def test_top_level_file_uses_multipart():
    s = _S()
    f = BufferedInputFile(b"data", "a.txt")
    params, files = s.prepare_request({"chat_id": 2, "photo": f, "caption": "c"})
    assert "photo" in files
    assert "photo" not in params
    assert params["caption"] == "c"


def test_media_group_attach_references():
    s = _S()
    media = [InputMediaPhoto(media=BufferedInputFile(b"x", "p.jpg"), caption="cap")]
    params, files = s.prepare_request({"chat_id": 3, "media": media})
    assert params["media"][0]["media"].startswith("attach://")
    assert len(files) == 1
    # multipart encoding turns lists into JSON strings
    encoded = s.encode_multipart_value(params["media"])
    assert encoded.startswith("[") and "attach://" in encoded


def test_error_mapping():
    import pytest

    from baleio.exceptions import BaleBadRequest, BaleRetryAfter

    s = _S()
    with pytest.raises(BaleBadRequest):
        s.check_response("sendMessage", 400, {"ok": False, "description": "bad", "error_code": 400})
    with pytest.raises(BaleRetryAfter):
        s.check_response(
            "sendMessage",
            429,
            {"ok": False, "description": "flood", "parameters": {"retry_after": 5}},
        )
