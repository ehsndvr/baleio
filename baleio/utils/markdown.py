"""Markdown helpers for Bale's formatting rules.

Bale renders every message as Markdown, but with a quirk: bold (``*``) and
italic (``_``) markers must have a **space before the opening and after the
closing** marker. These helpers add that padding for you.
"""
from __future__ import annotations


def bold(text: str) -> str:
    """*text* — note Bale needs surrounding spaces to render bold."""
    return f" *{text}* "


def italic(text: str) -> str:
    """_text_ — italic/emphasis."""
    return f" _{text}_ "


def link(text: str, url: str) -> str:
    """[text](url)"""
    return f"[{text}]({url})"


def instant_view(text: str, description: str) -> str:
    """```[text]description``` — Bale's 'instant view' annotation."""
    return f"```[{text}]{description}```"


def code(text: str) -> str:
    return f"`{text}`"


def pre(text: str) -> str:
    return f"```\n{text}\n```"
