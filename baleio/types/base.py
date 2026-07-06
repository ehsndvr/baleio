"""Base class for every API object.

Objects are Pydantic models. They optionally carry a reference to the ``Bot``
that produced them so that shortcut methods (``message.answer(...)`` and
friends) can call the API without the user passing the bot around.

The bot reference is resolved from, in order:
1. an explicit per-instance binding set via :meth:`BaleObject.as_`;
2. a :class:`contextvars.ContextVar` that the client and dispatcher set while
   a request is in flight or an update is being handled.
"""
from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING, Any, Optional

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from ..client.bot import Bot

#: Set by ``Bot.__call__`` and ``Dispatcher.feed_update`` for the duration of a
#: request / update so nested objects can find the active bot.
bot_context: ContextVar[Optional["Bot"]] = ContextVar("bale_bot_context", default=None)


class BaleObject(BaseModel):
    """Base for all Bale API objects and methods."""

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        arbitrary_types_allowed=True,
        defer_build=True,
        validate_assignment=True,
    )

    def __init__(self, **data: Any) -> None:
        # allow passing the owning bot positionally-less via ``_bot`` kwarg
        bot = data.pop("_bot", None)
        super().__init__(**data)
        if bot is not None:
            object.__setattr__(self, "_bound_bot", bot)

    _bound_bot: Optional["Bot"] = None

    def as_(self, bot: "Bot") -> "BaleObject":
        """Bind this object to a concrete bot and return it (chainable)."""
        object.__setattr__(self, "_bound_bot", bot)
        return self

    @property
    def bot(self) -> "Bot":
        bot = getattr(self, "_bound_bot", None) or bot_context.get()
        if bot is None:
            raise RuntimeError(
                f"{type(self).__name__} is not bound to a Bot instance. "
                "Access it inside a handler or bind it with `.as_(bot)`."
            )
        return bot

    def model_dump_api(self) -> dict[str, Any]:
        """Dump for sending to the API: aliases, no ``None`` values."""
        return self.model_dump(mode="json", by_alias=True, exclude_none=True)

    def __str__(self) -> str:
        fields = ", ".join(
            f"{k}={v!r}"
            for k, v in self.model_dump(exclude_none=True).items()
            if not k.startswith("_")
        )
        return f"{type(self).__name__}({fields})"


class MutableBaleObject(BaleObject):
    """Object whose fields are expected to be mutated after construction."""

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        arbitrary_types_allowed=True,
        defer_build=True,
        validate_assignment=False,
    )
