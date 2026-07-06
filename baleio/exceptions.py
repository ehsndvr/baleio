"""Exception hierarchy for baleio.

Mirrors aiogram's error model so migration is familiar.
"""
from __future__ import annotations

from typing import Any, Optional


class BaleError(Exception):
    """Base class for every exception raised by baleio."""


class DetailedBaleError(BaleError):
    """Base for errors that carry a human readable ``message``."""

    url: Optional[str] = None

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def __str__(self) -> str:
        message = self.message
        if self.url:
            message += f"\n(background on this error at: {self.url})"
        return message

    def __repr__(self) -> str:
        return f"{type(self).__name__}('{self}')"


class BaleNetworkError(DetailedBaleError):
    """Raised for connection/transport level problems."""


class BaleRetryAfter(DetailedBaleError):
    """Raised when the API asks us to slow down (flood control)."""

    url = "https://docs.bale.ai/"

    def __init__(self, retry_after: int) -> None:
        super().__init__(
            message=f"Flood control exceeded on request. Retry in {retry_after} seconds."
        )
        self.retry_after = retry_after


class ClientDecodeError(BaleError):
    """Raised when the server response cannot be decoded as JSON."""

    def __init__(self, message: str, original: Exception, data: Any) -> None:
        super().__init__()
        self.message = message
        self.original = original
        self.data = data

    def __str__(self) -> str:
        return f"{self.message}\nCaused from error: '{self.original!r}'\nby data: {self.data}"


class BaleAPIError(DetailedBaleError):
    """Raised when the Bale API returns ``ok = false``.

    Attributes:
        method: the method object that produced the error.
        message: description returned by the server.
    """

    label: str = "Bale server says"

    def __init__(
        self,
        method: Any,
        message: str,
        error_code: Optional[int] = None,
    ) -> None:
        super().__init__(message=message)
        self.method = method
        self.error_code = error_code

    def __str__(self) -> str:
        original = super().__str__()
        code = f" [{self.error_code}]" if self.error_code is not None else ""
        return f"{self.label}{code}: {original}"


class BaleBadRequest(BaleAPIError):
    pass


class BaleNotFound(BaleAPIError):
    pass


class BaleUnauthorized(BaleAPIError):
    pass


class BaleForbidden(BaleAPIError):
    pass


class BaleConflictError(BaleAPIError):
    pass


class BaleEntityTooLarge(BaleAPIError):
    pass


class BaleServerError(BaleAPIError):
    pass


class RestartingBale(BaleError):
    """Internal signal used to restart polling."""


class SceneException(BaleError):
    pass
