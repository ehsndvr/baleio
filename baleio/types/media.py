from __future__ import annotations

from typing import Optional

from .base import BaleObject


class PhotoSize(BaleObject):
    """One size of a photo or a file/sticker thumbnail."""

    file_id: str
    file_unique_id: Optional[str] = None
    width: int
    height: int
    file_size: Optional[int] = None


class Animation(BaleObject):
    file_id: str
    file_unique_id: Optional[str] = None
    width: int
    height: int
    duration: int
    thumbnail: Optional[PhotoSize] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


class Audio(BaleObject):
    file_id: str
    file_unique_id: Optional[str] = None
    duration: int
    title: Optional[str] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


class Document(BaleObject):
    file_id: str
    file_unique_id: Optional[str] = None
    thumbnail: Optional[PhotoSize] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


class Video(BaleObject):
    file_id: str
    file_unique_id: Optional[str] = None
    width: int
    height: int
    duration: int
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


class Voice(BaleObject):
    file_id: str
    file_unique_id: Optional[str] = None
    duration: Optional[int] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


class Sticker(BaleObject):
    file_id: str
    file_unique_id: Optional[str] = None
    type: Optional[str] = None
    width: int
    height: int
    thumbnail: Optional[PhotoSize] = None
    file_size: Optional[int] = None


class StickerSet(BaleObject):
    name: str
    title: str
    stickers: list[Sticker] = []
    thumbnail: Optional[PhotoSize] = None


class File(BaleObject):
    """A file ready to be downloaded via ``bot.get_file`` / ``bot.download``."""

    file_id: str
    file_unique_id: Optional[str] = None
    file_size: Optional[int] = None
    file_path: Optional[str] = None


class ChatPhoto(BaleObject):
    small_file_id: str
    small_file_unique_id: Optional[str] = None
    big_file_id: str
    big_file_unique_id: Optional[str] = None
