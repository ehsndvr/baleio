from __future__ import annotations

from typing import Optional, Union

from ..enums import InputMediaType
from .base import BaleObject
from .input_file import InputFile


class InputMedia(BaleObject):
    """Base for media items sent as part of an album (``sendMediaGroup``).

    ``media`` may be a ``file_id``, an HTTP URL, an ``attach://name`` reference
    or an :class:`InputFile` (which is uploaded and referenced automatically).
    """

    type: str
    media: Union[str, InputFile]
    caption: Optional[str] = None


class InputMediaPhoto(InputMedia):
    type: str = InputMediaType.PHOTO.value


class InputMediaVideo(InputMedia):
    type: str = InputMediaType.VIDEO.value
    thumbnail: Optional[Union[str, InputFile]] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None


class InputMediaAnimation(InputMedia):
    type: str = InputMediaType.ANIMATION.value
    thumbnail: Optional[Union[str, InputFile]] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None


class InputMediaAudio(InputMedia):
    type: str = InputMediaType.AUDIO.value
    thumbnail: Optional[Union[str, InputFile]] = None
    duration: Optional[int] = None
    title: Optional[str] = None


class InputMediaDocument(InputMedia):
    type: str = InputMediaType.DOCUMENT.value
    thumbnail: Optional[Union[str, InputFile]] = None


class InputSticker(BaleObject):
    """A sticker to add to a set."""

    sticker: Union[str, InputFile]
    emoji_list: Optional[list[str]] = None
