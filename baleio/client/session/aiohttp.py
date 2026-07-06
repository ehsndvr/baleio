"""aiohttp-backed HTTP session."""
from __future__ import annotations

import asyncio
import ssl
from typing import TYPE_CHECKING, Any, AsyncGenerator, Optional

import aiohttp
import certifi

from ...exceptions import BaleNetworkError, ClientDecodeError
from ...types.input_file import InputFile
from .base import BaseSession

if TYPE_CHECKING:
    from ..bot import Bot


class AiohttpSession(BaseSession):
    """Concrete session that talks to Bale over ``aiohttp``."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._session: Optional[aiohttp.ClientSession] = None
        self._connector_init = {"ssl": ssl.create_default_context(cafile=certifi.where())}
        self._should_reset_connector = True

    async def aiohttp_session(self) -> aiohttp.ClientSession:
        if self._should_reset_connector:
            await self.close()
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(**self._connector_init),
            )
            self._should_reset_connector = False
        return self._session

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()
            # allow the underlying SSL connections to close gracefully
            await asyncio.sleep(0.05)
        self._session = None

    def _build_form(
        self, params: dict[str, Any], files: dict[str, InputFile], bot: "Bot"
    ) -> aiohttp.FormData:
        form = aiohttp.FormData(quote_fields=False)
        for key, value in params.items():
            form.add_field(key, self.encode_multipart_value(value))
        for name, file in files.items():
            form.add_field(
                name,
                self._file_reader(bot, file),
                filename=file.filename or name,
            )
        return form

    @staticmethod
    async def _file_reader(bot: "Bot", file: InputFile) -> AsyncGenerator[bytes, None]:
        async for chunk in file.read(bot):
            yield chunk

    async def make_request(
        self,
        bot: "Bot",
        method: str,
        data: dict[str, Any],
        timeout: Optional[float] = None,
    ) -> Any:
        session = await self.aiohttp_session()
        url = self.api_endpoint(bot.token, method)
        params, files = self.prepare_request(data)
        request_timeout = aiohttp.ClientTimeout(total=timeout or self.timeout)

        kwargs: dict[str, Any] = {"timeout": request_timeout}
        if files:
            kwargs["data"] = self._build_form(params, files, bot)
        else:
            kwargs["json"] = params

        try:
            async with session.post(url, **kwargs) as response:
                raw = await response.text()
                decoded = self._decode(method, raw)
                return self.check_response(
                    method=method, status_code=response.status, content=decoded
                )
        except asyncio.TimeoutError:
            raise BaleNetworkError(f"Request timeout for method '{method}'")
        except aiohttp.ClientError as error:
            raise BaleNetworkError(
                f"aiohttp client error while calling '{method}': {error!r}"
            )

    @staticmethod
    def _decode(method: str, raw: str) -> dict[str, Any]:
        import json

        try:
            return json.loads(raw)
        except ValueError as error:
            raise ClientDecodeError(
                f"Failed to decode response for '{method}'", error, raw
            )

    async def stream_file(
        self, bot: "Bot", url: str, timeout: Optional[float] = None
    ) -> AsyncGenerator[bytes, None]:
        session = await self.aiohttp_session()
        request_timeout = aiohttp.ClientTimeout(total=timeout or self.timeout)
        async with session.get(url, timeout=request_timeout) as response:
            response.raise_for_status()
            async for chunk in response.content.iter_chunked(64 * 1024):
                yield chunk
