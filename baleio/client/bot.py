"""The :class:`Bot` — a typed async client for the Bale bot API."""
from __future__ import annotations

import os
import re
from typing import Any, BinaryIO, Optional, Union

from ..enums import ChatAction
from ..exceptions import BaleError
from ..types import (
    ChatFullInfo,
    File,
    InputFile,
    InputMedia,
    LabeledPrice,
    Message,
    MessageId,
    ReplyMarkup,
    Transaction,
    Update,
    User,
    WebhookInfo,
)
from ..types.base import BaleObject, bot_context
from ..types.chat import ChatMember, parse_chat_member
from .default import DefaultBotProperties
from .session import AiohttpSession, BaseSession

ChatId = Union[int, str]
FileInput = Union[InputFile, str]

_TOKEN_RE = re.compile(r"^\d+:[\w-]+$")


class Bot:
    """A Bale bot.

    Example::

        bot = Bot("123:token")
        me = await bot.get_me()
        await bot.send_message(chat_id, "hello")
    """

    def __init__(
        self,
        token: str,
        session: Optional[BaseSession] = None,
        default: Optional[DefaultBotProperties] = None,
        validate_token: bool = True,
    ) -> None:
        if validate_token:
            self.validate_token(token)
        self.token = token
        self.session = session or AiohttpSession()
        self.default = default or DefaultBotProperties()
        self._me: Optional[User] = None

    # ------------------------------------------------------------------ core
    @staticmethod
    def validate_token(token: str) -> None:
        if not isinstance(token, str) or not _TOKEN_RE.match(token.strip()):
            raise BaleError(
                "Invalid bot token. Expected a value like '123456789:XXXXXXXX'."
            )

    @property
    def id(self) -> int:
        """Numeric id parsed from the token."""
        return int(self.token.split(":", 1)[0])

    async def __call__(self, method: str, data: Optional[dict[str, Any]] = None) -> Any:
        """Low-level: call ``method`` and return the raw ``result`` field."""
        token = bot_context.set(self)
        try:
            return await self.session.make_request(self, method, data or {})
        finally:
            bot_context.reset(token)

    async def close(self) -> None:
        await self.session.close()

    async def __aenter__(self) -> "Bot":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    # --- result binding ----------------------------------------------------
    def _bind(self, obj: Any) -> Any:
        """Recursively attach ``self`` to every object so shortcuts work."""
        if isinstance(obj, BaleObject):
            object.__setattr__(obj, "_bound_bot", self)
            for value in obj.__dict__.values():
                self._bind(value)
        elif isinstance(obj, list):
            for item in obj:
                self._bind(item)
        return obj

    def _message(self, result: Any) -> Message:
        return self._bind(Message.model_validate(result))

    # =============================================================== updates
    async def get_updates(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> list[Update]:
        result = await self("getUpdates", {"offset": offset, "limit": limit, "timeout": timeout})
        return [self._bind(Update.model_validate(item)) for item in result or []]

    async def set_webhook(self, url: str) -> bool:
        return await self("setWebhook", {"url": url})

    async def delete_webhook(self) -> bool:
        return await self("deleteWebhook")

    async def get_webhook_info(self) -> WebhookInfo:
        return self._bind(WebhookInfo.model_validate(await self("getWebhookInfo")))

    # ================================================================== base
    async def get_me(self) -> User:
        self._me = self._bind(User.model_validate(await self("getMe")))
        return self._me

    async def me(self) -> User:
        """Cached :meth:`get_me`."""
        if self._me is None:
            await self.get_me()
        assert self._me is not None
        return self._me

    # =============================================================== sending
    async def send_message(
        self,
        chat_id: ChatId,
        text: str,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        return self._message(
            await self(
                "sendMessage",
                {
                    "chat_id": chat_id,
                    "text": text,
                    "reply_to_message_id": reply_to_message_id,
                    "reply_markup": reply_markup,
                },
            )
        )

    async def forward_message(
        self, chat_id: ChatId, from_chat_id: ChatId, message_id: int
    ) -> Message:
        return self._message(
            await self(
                "forwardMessage",
                {"chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id},
            )
        )

    async def copy_message(
        self, chat_id: ChatId, from_chat_id: ChatId, message_id: int
    ) -> MessageId:
        result = await self(
            "copyMessage",
            {"chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id},
        )
        return self._bind(MessageId.model_validate(result))

    async def send_photo(
        self,
        chat_id: ChatId,
        photo: FileInput,
        caption: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        return self._message(
            await self(
                "sendPhoto",
                {
                    "chat_id": chat_id,
                    "photo": photo,
                    "caption": caption,
                    "reply_to_message_id": reply_to_message_id,
                    "reply_markup": reply_markup,
                },
            )
        )

    async def send_audio(
        self,
        chat_id: ChatId,
        audio: FileInput,
        caption: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        return self._message(
            await self(
                "sendAudio",
                {
                    "chat_id": chat_id,
                    "audio": audio,
                    "caption": caption,
                    "reply_to_message_id": reply_to_message_id,
                    "reply_markup": reply_markup,
                },
            )
        )

    async def send_document(
        self,
        chat_id: ChatId,
        document: FileInput,
        caption: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        return self._message(
            await self(
                "sendDocument",
                {
                    "chat_id": chat_id,
                    "document": document,
                    "caption": caption,
                    "reply_to_message_id": reply_to_message_id,
                    "reply_markup": reply_markup,
                },
            )
        )

    async def send_video(
        self,
        chat_id: ChatId,
        video: FileInput,
        caption: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        return self._message(
            await self(
                "sendVideo",
                {
                    "chat_id": chat_id,
                    "video": video,
                    "caption": caption,
                    "reply_to_message_id": reply_to_message_id,
                    "reply_markup": reply_markup,
                },
            )
        )

    async def send_animation(
        self,
        chat_id: ChatId,
        animation: FileInput,
        caption: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        return self._message(
            await self(
                "sendAnimation",
                {
                    "chat_id": chat_id,
                    "animation": animation,
                    "caption": caption,
                    "reply_to_message_id": reply_to_message_id,
                    "reply_markup": reply_markup,
                },
            )
        )

    async def send_voice(
        self,
        chat_id: ChatId,
        voice: FileInput,
        caption: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        return self._message(
            await self(
                "sendVoice",
                {
                    "chat_id": chat_id,
                    "voice": voice,
                    "caption": caption,
                    "reply_to_message_id": reply_to_message_id,
                    "reply_markup": reply_markup,
                },
            )
        )

    async def send_media_group(
        self,
        chat_id: ChatId,
        media: list[InputMedia],
        reply_to_message_id: Optional[int] = None,
    ) -> list[Message]:
        result = await self(
            "sendMediaGroup",
            {"chat_id": chat_id, "media": media, "reply_to_message_id": reply_to_message_id},
        )
        return [self._bind(Message.model_validate(item)) for item in result or []]

    async def send_location(
        self,
        chat_id: ChatId,
        latitude: float,
        longitude: float,
        horizontal_accuracy: Optional[float] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        return self._message(
            await self(
                "sendLocation",
                {
                    "chat_id": chat_id,
                    "latitude": latitude,
                    "longitude": longitude,
                    "horizontal_accuracy": horizontal_accuracy,
                    "reply_to_message_id": reply_to_message_id,
                    "reply_markup": reply_markup,
                },
            )
        )

    async def send_contact(
        self,
        chat_id: ChatId,
        phone_number: str,
        first_name: str,
        last_name: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        return self._message(
            await self(
                "sendContact",
                {
                    "chat_id": chat_id,
                    "phone_number": phone_number,
                    "first_name": first_name,
                    "last_name": last_name,
                    "reply_to_message_id": reply_to_message_id,
                    "reply_markup": reply_markup,
                },
            )
        )

    async def send_chat_action(
        self, chat_id: ChatId, action: Union[str, ChatAction]
    ) -> bool:
        return await self("sendChatAction", {"chat_id": chat_id, "action": action})

    # =============================================================== queries
    async def get_file(self, file_id: str) -> File:
        return self._bind(File.model_validate(await self("getFile", {"file_id": file_id})))

    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: Optional[bool] = None,
    ) -> bool:
        return await self(
            "answerCallbackQuery",
            {
                "callback_query_id": callback_query_id,
                "text": text,
                "show_alert": show_alert,
            },
        )

    async def ask_review(self, user_id: int, delay_seconds: int) -> bool:
        return await self(
            "askReview", {"user_id": user_id, "delay_seconds": delay_seconds}
        )

    # =========================================================== chat admin
    async def ban_chat_member(self, chat_id: ChatId, user_id: int) -> bool:
        return await self("banChatMember", {"chat_id": chat_id, "user_id": user_id})

    async def unban_chat_member(
        self, chat_id: ChatId, user_id: int, only_if_banned: Optional[bool] = None
    ) -> bool:
        return await self(
            "unbanChatMember",
            {"chat_id": chat_id, "user_id": user_id, "only_if_banned": only_if_banned},
        )

    async def promote_chat_member(
        self,
        chat_id: ChatId,
        user_id: int,
        can_change_info: Optional[bool] = None,
        can_post_messages: Optional[bool] = None,
        can_edit_messages: Optional[bool] = None,
        can_delete_messages: Optional[bool] = None,
        can_manage_video_chats: Optional[bool] = None,
        can_invite_users: Optional[bool] = None,
        can_restrict_members: Optional[bool] = None,
    ) -> bool:
        return await self(
            "promoteChatMember",
            {
                "chat_id": chat_id,
                "user_id": user_id,
                "can_change_info": can_change_info,
                "can_post_messages": can_post_messages,
                "can_edit_messages": can_edit_messages,
                "can_delete_messages": can_delete_messages,
                "can_manage_video_chats": can_manage_video_chats,
                "can_invite_users": can_invite_users,
                "can_restrict_members": can_restrict_members,
            },
        )

    async def set_chat_photo(self, chat_id: ChatId, photo: InputFile) -> bool:
        return await self("setChatPhoto", {"chat_id": chat_id, "photo": photo})

    async def leave_chat(self, chat_id: ChatId) -> bool:
        return await self("leaveChat", {"chat_id": chat_id})

    async def get_chat(self, chat_id: ChatId) -> ChatFullInfo:
        return self._bind(ChatFullInfo.model_validate(await self("getChat", {"chat_id": chat_id})))

    async def get_chat_administrators(self, chat_id: ChatId) -> list[ChatMember]:
        result = await self("getChatAdministrators", {"chat_id": chat_id})
        return [self._bind(parse_chat_member(item)) for item in result or []]

    async def get_chat_members_count(self, chat_id: ChatId) -> int:
        return await self("getChatMembersCount", {"chat_id": chat_id})

    async def get_chat_member(self, chat_id: ChatId, user_id: int) -> ChatMember:
        result = await self("getChatMember", {"chat_id": chat_id, "user_id": user_id})
        return self._bind(parse_chat_member(result))

    async def pin_chat_message(self, chat_id: ChatId, message_id: int) -> bool:
        return await self("pinChatMessage", {"chat_id": chat_id, "message_id": message_id})

    async def unpin_chat_message(self, chat_id: ChatId, message_id: int) -> bool:
        return await self("unPinChatMessage", {"chat_id": chat_id, "message_id": message_id})

    async def unpin_all_chat_messages(self, chat_id: ChatId) -> bool:
        return await self("unpinAllChatMessages", {"chat_id": chat_id})

    async def set_chat_title(self, chat_id: ChatId, title: str) -> bool:
        return await self("setChatTitle", {"chat_id": chat_id, "title": title})

    async def set_chat_description(self, chat_id: ChatId, description: str) -> bool:
        return await self("setChatDescription", {"chat_id": chat_id, "description": description})

    async def delete_chat_photo(self, chat_id: ChatId) -> bool:
        return await self("deleteChatPhoto", {"chat_id": chat_id})

    async def create_chat_invite_link(self, chat_id: ChatId) -> Any:
        return await self("createChatInviteLink", {"chat_id": chat_id})

    async def revoke_chat_invite_link(self, chat_id: ChatId, invite_link: str) -> Any:
        return await self(
            "revokeChatInviteLink", {"chat_id": chat_id, "invite_link": invite_link}
        )

    async def export_chat_invite_link(self, chat_id: ChatId) -> str:
        return await self("exportChatInviteLink", {"chat_id": chat_id})

    # ============================================================ edit / del
    async def edit_message_text(
        self,
        chat_id: ChatId,
        message_id: int,
        text: str,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Union[Message, bool]:
        result = await self(
            "editMessageText",
            {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text,
                "reply_markup": reply_markup,
            },
        )
        return self._message(result) if isinstance(result, dict) else result

    async def edit_message_caption(
        self,
        chat_id: ChatId,
        message_id: int,
        caption: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Union[Message, bool]:
        result = await self(
            "editMessageCaption",
            {
                "chat_id": chat_id,
                "message_id": message_id,
                "caption": caption,
                "reply_markup": reply_markup,
            },
        )
        return self._message(result) if isinstance(result, dict) else result

    async def edit_message_reply_markup(
        self,
        chat_id: ChatId,
        message_id: int,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Union[Message, bool]:
        result = await self(
            "editMessageReplyMarkup",
            {"chat_id": chat_id, "message_id": message_id, "reply_markup": reply_markup},
        )
        return self._message(result) if isinstance(result, dict) else result

    async def delete_message(self, chat_id: ChatId, message_id: int) -> bool:
        return await self("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

    # ============================================================== stickers
    async def upload_sticker_file(self, user_id: int, sticker: InputFile) -> Any:
        return await self("uploadStickerFile", {"user_id": user_id, "sticker": sticker})

    async def create_new_sticker_set(
        self, user_id: int, name: str, title: str, sticker: list[Any]
    ) -> bool:
        return await self(
            "createNewStickerSet",
            {"user_id": user_id, "name": name, "title": title, "sticker": sticker},
        )

    async def add_sticker_to_set(self, user_id: int, name: str, sticker: Any) -> bool:
        return await self(
            "addStickerToSet", {"user_id": user_id, "name": name, "sticker": sticker}
        )

    # ============================================================== payments
    async def send_invoice(
        self,
        chat_id: ChatId,
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        prices: list[LabeledPrice],
        photo_url: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
    ) -> Message:
        return self._message(
            await self(
                "sendInvoice",
                {
                    "chat_id": chat_id,
                    "title": title,
                    "description": description,
                    "payload": payload,
                    "provider_token": provider_token,
                    "prices": prices,
                    "photo_url": photo_url,
                    "reply_to_message_id": reply_to_message_id,
                },
            )
        )

    async def create_invoice_link(
        self,
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        prices: list[LabeledPrice],
    ) -> str:
        return await self(
            "createInvoiceLink",
            {
                "title": title,
                "description": description,
                "payload": payload,
                "provider_token": provider_token,
                "prices": prices,
            },
        )

    async def answer_pre_checkout_query(
        self,
        pre_checkout_query_id: str,
        ok: bool,
        error_message: Optional[str] = None,
    ) -> bool:
        return await self(
            "answerPreCheckoutQuery",
            {
                "pre_checkout_query_id": pre_checkout_query_id,
                "ok": ok,
                "error_message": error_message,
            },
        )

    async def inquire_transaction(self, transaction_id: str) -> Transaction:
        result = await self("inquireTransaction", {"transaction_id": transaction_id})
        return self._bind(Transaction.model_validate(result))

    # ================================================================ files
    def get_file_url(self, file_path: str) -> str:
        return self.session.file_url(self.token, file_path)

    async def download_file(
        self,
        file_path: str,
        destination: Optional[Union[str, os.PathLike, BinaryIO]] = None,
    ) -> Optional[bytes]:
        """Download a file by its ``file_path`` (from :meth:`get_file`)."""
        url = self.get_file_url(file_path)
        chunks: list[bytes] = []
        writer: Optional[BinaryIO] = None
        opened = False
        if isinstance(destination, (str, os.PathLike)):
            writer = open(destination, "wb")
            opened = True
        elif destination is not None:
            writer = destination
        try:
            async for chunk in self.session.stream_file(self, url):
                if writer is not None:
                    writer.write(chunk)
                else:
                    chunks.append(chunk)
        finally:
            if opened and writer is not None:
                writer.close()
        return None if writer is not None else b"".join(chunks)

    async def download(
        self,
        file: Union[str, File],
        destination: Optional[Union[str, os.PathLike, BinaryIO]] = None,
    ) -> Optional[bytes]:
        """Download a file given its ``file_id`` or a :class:`File` object."""
        if isinstance(file, File):
            file_obj = file
        else:
            file_obj = await self.get_file(file)
        if not file_obj.file_path:
            raise BaleError("File has no file_path; cannot download.")
        return await self.download_file(file_obj.file_path, destination)

    def __repr__(self) -> str:
        return f"<Bot id={self.id}>"
