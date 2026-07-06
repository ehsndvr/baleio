from __future__ import annotations

from .base import BaleObject
from .update import Update


class ErrorEvent(BaleObject):
    """Passed to ``@dp.errors()`` handlers when processing an update raises.

    Exposes ``update`` (the update that was being handled when the error occurred)
    and ``exception`` (the exception that was raised).
    """

    update: Update
    exception: Exception

    model_config = {
        **BaleObject.model_config,
        "arbitrary_types_allowed": True,
    }
