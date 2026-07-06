from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Union

from pydantic import AliasChoices, Field

from ..enums import ContentType
from .attachments import (
    Contact,
    Invoice,
    Location,
    MessageEntity,
    WebAppData,
)
from .base import BaleObject
from .chat import Chat
from .keyboards import InlineKeyboardMarkup
from .media import Animation, Audio, Document, PhotoSize, Sticker, Video, Voice
from .payments import SuccessfulPayment
from .user import User

if TYPE_CHECKING:
    from .keyboards import ReplyMarkup

#: sentinel so ``send_copy`` can tell "keep original markup" from "remove it"
_KEEP = object()


class Message(BaleObject):
    """A message. Carries the richest set of shortcut methods in the library."""

    message_id: int
    date: Optional[int] = None
    chat: Chat
    from_user: Optional[User] = Field(
        default=None, validation_alias=AliasChoices("from_user", "from")
    )
    sender_chat: Optional[Chat] = None
    forward_from: Optional[User] = None
    forward_from_chat: Optional[Chat] = None
    forward_from_message_id: Optional[int] = None
    forward_date: Optional[int] = None
    reply_to_message: Optional["Message"] = None
    edit_date: Optional[int] = None
    media_group_id: Optional[str] = None
    text: Optional[str] = None
    entities: Optional[list[MessageEntity]] = None
    caption: Optional[str] = None
    caption_entities: Optional[list[MessageEntity]] = None
    animation: Optional[Animation] = None
    audio: Optional[Audio] = None
    document: Optional[Document] = None
    photo: Optional[list[PhotoSize]] = None
    sticker: Optional[Sticker] = None
    video: Optional[Video] = None
    voice: Optional[Voice] = None
    contact: Optional[Contact] = None
    location: Optional[Location] = None
    new_chat_members: Optional[list[User]] = None
    left_chat_member: Optional[User] = None
    invoice: Optional[Invoice] = None
    successful_payment: Optional[SuccessfulPayment] = None
    web_app_data: Optional[WebAppData] = None
    reply_markup: Optional["InlineKeyboardMarkup"] = None

    # ---- convenience -----------------------------------------------------
    @property
    def content_type(self) -> str:
        """Best-effort detection of the message content type."""
        if self.text is not None:
            return ContentType.TEXT
        if self.animation is not None:
            return ContentType.ANIMATION
        if self.audio is not None:
            return ContentType.AUDIO
        if self.document is not None:
            return ContentType.DOCUMENT
        if self.photo is not None:
            return ContentType.PHOTO
        if self.sticker is not None:
            return ContentType.STICKER
        if self.video is not None:
            return ContentType.VIDEO
        if self.voice is not None:
            return ContentType.VOICE
        if self.contact is not None:
            return ContentType.CONTACT
        if self.location is not None:
            return ContentType.LOCATION
        if self.invoice is not None:
            return ContentType.INVOICE
        if self.successful_payment is not None:
            return ContentType.SUCCESSFUL_PAYMENT
        if self.new_chat_members is not None:
            return ContentType.NEW_CHAT_MEMBERS
        if self.left_chat_member is not None:
            return ContentType.LEFT_CHAT_MEMBER
        if self.web_app_data is not None:
            return ContentType.WEB_APP_DATA
        return ContentType.UNKNOWN

    def get_args(self) -> Optional[str]:
        """Return the text after the first ``/command``, if any."""
        text = self.text or self.caption
        if not text:
            return None
        parts = text.split(maxsplit=1)
        return parts[1] if len(parts) > 1 else None

    # ---- shortcut methods -------------------------------------------------
    async def answer(
        self,
        text: str,
        reply_markup: Optional["ReplyMarkup"] = None,
        **kwargs: Any,
    ) -> "Message":
        """Send a new message to the same chat."""
        return await self.bot.send_message(
            self.chat.id, text, reply_markup=reply_markup, **kwargs
        )

    async def reply(
        self,
        text: str,
        reply_markup: Optional["ReplyMarkup"] = None,
        **kwargs: Any,
    ) -> "Message":
        """Reply to this message in the same chat."""
        return await self.bot.send_message(
            self.chat.id,
            text,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs,
        )

    async def answer_photo(self, photo: Any, **kwargs: Any) -> "Message":
        return await self.bot.send_photo(self.chat.id, photo, **kwargs)

    async def reply_photo(self, photo: Any, **kwargs: Any) -> "Message":
        return await self.bot.send_photo(
            self.chat.id, photo, reply_to_message_id=self.message_id, **kwargs
        )

    async def answer_document(self, document: Any, **kwargs: Any) -> "Message":
        return await self.bot.send_document(self.chat.id, document, **kwargs)

    async def answer_video(self, video: Any, **kwargs: Any) -> "Message":
        return await self.bot.send_video(self.chat.id, video, **kwargs)

    async def answer_audio(self, audio: Any, **kwargs: Any) -> "Message":
        return await self.bot.send_audio(self.chat.id, audio, **kwargs)

    async def answer_animation(self, animation: Any, **kwargs: Any) -> "Message":
        return await self.bot.send_animation(self.chat.id, animation, **kwargs)

    async def answer_voice(self, voice: Any, **kwargs: Any) -> "Message":
        return await self.bot.send_voice(self.chat.id, voice, **kwargs)

    async def answer_location(
        self, latitude: float, longitude: float, **kwargs: Any
    ) -> "Message":
        return await self.bot.send_location(self.chat.id, latitude, longitude, **kwargs)

    async def answer_contact(
        self, phone_number: str, first_name: str, **kwargs: Any
    ) -> "Message":
        return await self.bot.send_contact(
            self.chat.id, phone_number, first_name, **kwargs
        )

    async def edit_text(
        self, text: str, reply_markup: Optional["InlineKeyboardMarkup"] = None, **kwargs: Any
    ) -> Union["Message", bool]:
        return await self.bot.edit_message_text(
            self.chat.id, self.message_id, text, reply_markup=reply_markup, **kwargs
        )

    async def edit_caption(
        self, caption: str, reply_markup: Optional["InlineKeyboardMarkup"] = None, **kwargs: Any
    ) -> Union["Message", bool]:
        return await self.bot.edit_message_caption(
            self.chat.id, self.message_id, caption, reply_markup=reply_markup, **kwargs
        )

    async def edit_reply_markup(
        self, reply_markup: Optional["InlineKeyboardMarkup"] = None
    ) -> Union["Message", bool]:
        return await self.bot.edit_message_reply_markup(
            self.chat.id, self.message_id, reply_markup=reply_markup
        )

    async def delete(self) -> bool:
        return await self.bot.delete_message(self.chat.id, self.message_id)

    async def forward(self, chat_id: Union[int, str], **kwargs: Any) -> "Message":
        return await self.bot.forward_message(
            chat_id, self.chat.id, self.message_id, **kwargs
        )

    async def copy_to(self, chat_id: Union[int, str], **kwargs: Any) -> Any:
        return await self.bot.copy_message(
            chat_id, self.chat.id, self.message_id, **kwargs
        )

    async def send_copy(
        self,
        chat_id: Union[int, str],
        reply_markup: Any = _KEEP,
        **kwargs: Any,
    ) -> "Message":
        """Re-send this message's content to ``chat_id`` (aiogram-style).

        Unlike :meth:`copy_to` (which uses the ``copyMessage`` API), this rebuilds
        the message locally by dispatching to the matching ``send*`` method, so it
        works with ``file_id``\\ s already on Bale. Raises ``TypeError`` for content
        types Bale cannot re-send (e.g. stickers, invoices, service messages).
        """
        markup = self.reply_markup if reply_markup is _KEEP else reply_markup
        if self.text is not None:
            return await self.bot.send_message(
                chat_id, self.text, reply_markup=markup, **kwargs
            )
        if self.photo:
            return await self.bot.send_photo(
                chat_id, self.photo[-1].file_id, caption=self.caption,
                reply_markup=markup, **kwargs,
            )
        if self.video:
            return await self.bot.send_video(
                chat_id, self.video.file_id, caption=self.caption,
                reply_markup=markup, **kwargs,
            )
        if self.animation:
            return await self.bot.send_animation(
                chat_id, self.animation.file_id, caption=self.caption,
                reply_markup=markup, **kwargs,
            )
        if self.audio:
            return await self.bot.send_audio(
                chat_id, self.audio.file_id, caption=self.caption,
                reply_markup=markup, **kwargs,
            )
        if self.voice:
            return await self.bot.send_voice(
                chat_id, self.voice.file_id, caption=self.caption,
                reply_markup=markup, **kwargs,
            )
        if self.document:
            return await self.bot.send_document(
                chat_id, self.document.file_id, caption=self.caption,
                reply_markup=markup, **kwargs,
            )
        if self.location:
            return await self.bot.send_location(
                chat_id, self.location.latitude, self.location.longitude,
                reply_markup=markup, **kwargs,
            )
        if self.contact:
            return await self.bot.send_contact(
                chat_id, self.contact.phone_number, self.contact.first_name,
                last_name=self.contact.last_name, reply_markup=markup, **kwargs,
            )
        raise TypeError(
            f"Cannot send_copy a message with content_type={self.content_type!r}"
        )

    async def pin(self) -> bool:
        return await self.bot.pin_chat_message(self.chat.id, self.message_id)

    async def unpin(self) -> bool:
        return await self.bot.unpin_chat_message(self.chat.id, self.message_id)
