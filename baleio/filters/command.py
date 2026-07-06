"""The ``Command`` filter, e.g. ``@router.message(Command('start'))``."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Optional, Pattern, Sequence, Union

from ..types.message import Message
from .base import BaseFilter

CommandPatternType = Union[str, "re.Pattern[str]"]


@dataclass
class CommandObject:
    """The parsed pieces of a ``/command@bot args`` message."""

    prefix: str = "/"
    command: str = ""
    mention: Optional[str] = None
    args: Optional[str] = None

    @property
    def text(self) -> str:
        parts = [f"{self.prefix}{self.command}"]
        if self.mention:
            parts.append(f"@{self.mention}")
        if self.args:
            parts.append(f" {self.args}")
        return "".join(parts)


class Command(BaseFilter):
    def __init__(
        self,
        *commands: Union[str, Pattern],
        prefix: str = "/",
        ignore_case: bool = False,
        ignore_mention: bool = False,
    ) -> None:
        if not commands:
            raise ValueError("Command filter needs at least one command")
        self.prefix = prefix
        self.ignore_case = ignore_case
        self.ignore_mention = ignore_mention
        self.commands: list[Union[str, Pattern]] = []
        for command in commands:
            if isinstance(command, str) and ignore_case:
                self.commands.append(command.lower())
            else:
                self.commands.append(command)

    async def __call__(self, message: Any, **kwargs: Any) -> Union[bool, dict[str, Any]]:
        if not isinstance(message, Message):
            return False
        text = message.text or message.caption
        if not text:
            return False
        parsed = self._parse(text)
        if parsed is None:
            return False
        return {"command": parsed}

    def _parse(self, text: str) -> Optional[CommandObject]:
        if not text.startswith(self.prefix):
            return None
        head, _, args = text[len(self.prefix):].partition(" ")
        command, _, mention = head.partition("@")
        args = args.strip() or None

        candidate = command.lower() if self.ignore_case else command
        for expected in self.commands:
            if isinstance(expected, str):
                if candidate == expected:
                    return CommandObject(
                        prefix=self.prefix,
                        command=command,
                        mention=mention or None,
                        args=args,
                    )
            else:  # regex
                if expected.fullmatch(command):
                    return CommandObject(
                        prefix=self.prefix,
                        command=command,
                        mention=mention or None,
                        args=args,
                    )
        return None


class CommandStart(Command):
    """Shorthand for ``Command('start')``."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__("start", **kwargs)
