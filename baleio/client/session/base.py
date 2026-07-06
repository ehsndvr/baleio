"""Abstract HTTP session and request-serialization helpers."""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from enum import Enum
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Optional

from ...exceptions import (
    BaleAPIError,
    BaleBadRequest,
    BaleConflictError,
    BaleEntityTooLarge,
    BaleForbidden,
    BaleNotFound,
    BaleRetryAfter,
    BaleServerError,
    BaleUnauthorized,
)
from ...types.base import BaleObject
from ...types.input_file import InputFile
from ...types.input_media import InputMedia, InputSticker

if TYPE_CHECKING:
    from ..bot import Bot

DEFAULT_TIMEOUT = 60.0
PRODUCTION = "https://tapi.bale.ai"

_SKIP = object()


class BaleType:
    """Marker for how to interpret the ``result`` field of a response."""


class BaseSession(ABC):
    """Shared behaviour for concrete HTTP sessions."""

    def __init__(
        self,
        api_url: str = PRODUCTION,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout

    # --- URL helpers -------------------------------------------------------
    def api_endpoint(self, token: str, method: str) -> str:
        return f"{self.api_url}/bot{token}/{method}"

    def file_url(self, token: str, path: str) -> str:
        return f"{self.api_url}/file/bot{token}/{path}"

    # --- serialization -----------------------------------------------------
    def prepare_request(self, data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, InputFile]]:
        """Split ``data`` into JSON-able params and a mapping of files to upload."""
        files: dict[str, InputFile] = {}
        params: dict[str, Any] = {}
        for key, value in data.items():
            if value is None:
                continue
            prepared = self._prepare_value(key, value, files)
            if prepared is _SKIP:
                continue
            params[key] = prepared
        return params, files

    def _prepare_value(self, key: str, value: Any, files: dict[str, InputFile]) -> Any:
        if isinstance(value, InputFile):
            files[key] = value
            return _SKIP
        if isinstance(value, (InputMedia, InputSticker)):
            return self._prepare_media(value, files)
        if isinstance(value, list):
            return [self._prepare_item(item, files) for item in value]
        if isinstance(value, BaleObject):
            return value.model_dump(mode="json", by_alias=True, exclude_none=True)
        if isinstance(value, Enum):
            return value.value
        return value

    def _prepare_item(self, item: Any, files: dict[str, InputFile]) -> Any:
        if isinstance(item, (InputMedia, InputSticker)):
            return self._prepare_media(item, files)
        if isinstance(item, BaleObject):
            return item.model_dump(mode="json", by_alias=True, exclude_none=True)
        if isinstance(item, Enum):
            return item.value
        return item

    def _prepare_media(self, media: BaleObject, files: dict[str, InputFile]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for field, value in media.__dict__.items():
            if value is None:
                continue
            if isinstance(value, InputFile):
                name = f"attach_{len(files)}"
                files[name] = value
                result[field] = f"attach://{name}"
            elif isinstance(value, Enum):
                result[field] = value.value
            else:
                result[field] = value
        return result

    @staticmethod
    def encode_multipart_value(value: Any) -> str:
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, Enum):
            return str(value.value)
        return str(value)

    # --- response handling -------------------------------------------------
    def check_response(
        self, method: Any, status_code: int, content: dict[str, Any]
    ) -> Any:
        """Validate a decoded response envelope and return its ``result``."""
        if content.get("ok"):
            return content.get("result")

        description = content.get("description", "Unknown error")
        error_code = content.get("error_code")
        parameters = content.get("parameters") or {}
        retry_after = parameters.get("retry_after")
        if retry_after is not None:
            raise BaleRetryAfter(retry_after=retry_after)

        exc_type = self._exception_for(status_code, error_code)
        raise exc_type(method=method, message=description, error_code=error_code)

    @staticmethod
    def _exception_for(status_code: int, error_code: Optional[int]) -> type[BaleAPIError]:
        code = error_code or status_code
        mapping = {
            HTTPStatus.BAD_REQUEST: BaleBadRequest,
            HTTPStatus.UNAUTHORIZED: BaleUnauthorized,
            HTTPStatus.FORBIDDEN: BaleForbidden,
            HTTPStatus.NOT_FOUND: BaleNotFound,
            HTTPStatus.CONFLICT: BaleConflictError,
            HTTPStatus.REQUEST_ENTITY_TOO_LARGE: BaleEntityTooLarge,
        }
        if code in mapping:
            return mapping[code]
        if isinstance(code, int) and code >= 500:
            return BaleServerError
        return BaleAPIError

    # --- abstract ----------------------------------------------------------
    @abstractmethod
    async def make_request(
        self,
        bot: "Bot",
        method: str,
        data: dict[str, Any],
        timeout: Optional[float] = None,
    ) -> Any:
        """Perform the API call and return the decoded ``result``."""

    @abstractmethod
    async def stream_file(
        self, bot: "Bot", url: str, timeout: Optional[float] = None
    ) -> Any:
        """Yield chunks of a downloaded file."""

    @abstractmethod
    async def close(self) -> None:
        ...

    async def __aenter__(self) -> "BaseSession":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()
