"""File upload helpers.

A user may send a file three ways (per the Bale docs):
* a ``file_id`` string of an already-uploaded file;
* an HTTP URL string;
* a new upload — represented here by an :class:`InputFile` subclass.
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Optional, Union

DEFAULT_CHUNK_SIZE = 64 * 1024


class InputFile(ABC):
    """Abstract file to be uploaded via ``multipart/form-data``."""

    def __init__(
        self,
        filename: Optional[str] = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> None:
        self.filename = filename
        self.chunk_size = chunk_size

    @abstractmethod
    async def read(self, bot: Any) -> AsyncGenerator[bytes, None]:
        """Yield the file content in chunks."""
        yield b""  # pragma: no cover


class BufferedInputFile(InputFile):
    """A file backed by an in-memory ``bytes`` buffer."""

    def __init__(
        self,
        file: bytes,
        filename: str,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> None:
        super().__init__(filename=filename, chunk_size=chunk_size)
        self.data = file

    @classmethod
    def from_file(
        cls, path: Union[str, os.PathLike], filename: Optional[str] = None, **kwargs: Any
    ) -> "BufferedInputFile":
        with open(path, "rb") as f:
            data = f.read()
        return cls(data, filename=filename or os.path.basename(path), **kwargs)

    async def read(self, bot: Any) -> AsyncGenerator[bytes, None]:
        for i in range(0, len(self.data), self.chunk_size):
            yield self.data[i : i + self.chunk_size]


class FSInputFile(InputFile):
    """A file read lazily from the filesystem."""

    def __init__(
        self,
        path: Union[str, os.PathLike],
        filename: Optional[str] = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> None:
        super().__init__(filename=filename or os.path.basename(path), chunk_size=chunk_size)
        self.path = path

    async def read(self, bot: Any) -> AsyncGenerator[bytes, None]:
        # Read in a thread to avoid blocking the event loop on large files.
        import asyncio

        loop = asyncio.get_event_loop()
        with open(self.path, "rb") as f:
            while True:
                chunk = await loop.run_in_executor(None, f.read, self.chunk_size)
                if not chunk:
                    break
                yield chunk


class URLInputFile(InputFile):
    """A file the client downloads from ``url`` and re-uploads.

    Note: Bale also accepts a plain URL string for most ``send*`` methods, in
    which case *Bale itself* downloads the file. Use this class only when you
    want the bot to fetch and stream the bytes.
    """

    def __init__(
        self,
        url: str,
        filename: Optional[str] = None,
        headers: Optional[dict[str, Any]] = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> None:
        super().__init__(filename=filename, chunk_size=chunk_size)
        self.url = url
        self.headers = headers or {}

    async def read(self, bot: Any) -> AsyncGenerator[bytes, None]:
        session = await bot.session.aiohttp_session()
        async with session.get(self.url, headers=self.headers) as resp:
            async for chunk in resp.content.iter_chunked(self.chunk_size):
                yield chunk


__all__ = [
    "InputFile",
    "BufferedInputFile",
    "FSInputFile",
    "URLInputFile",
]
