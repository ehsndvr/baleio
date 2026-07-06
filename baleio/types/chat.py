from __future__ import annotations

from typing import Any, Optional, Union

from ..enums import ChatType
from .base import BaleObject
from .media import ChatPhoto
from .user import User


class Chat(BaleObject):
    """A chat (private, group or channel)."""

    id: int
    type: Optional[str] = None
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @property
    def full_name(self) -> str:
        if self.title:
            return self.title
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or (f"@{self.username}" if self.username else str(self.id))

    # ---- shortcut methods -------------------------------------------------
    async def ban(self, user_id: int, **kwargs: Any) -> bool:
        return await self.bot.ban_chat_member(self.id, user_id, **kwargs)

    async def unban(self, user_id: int, **kwargs: Any) -> bool:
        return await self.bot.unban_chat_member(self.id, user_id, **kwargs)

    async def leave(self) -> bool:
        return await self.bot.leave_chat(self.id)

    async def get_member(self, user_id: int) -> "ChatMember":
        return await self.bot.get_chat_member(self.id, user_id)

    async def get_administrators(self) -> list["ChatMember"]:
        return await self.bot.get_chat_administrators(self.id)

    async def get_member_count(self) -> int:
        return await self.bot.get_chat_members_count(self.id)

    async def set_title(self, title: str) -> bool:
        return await self.bot.set_chat_title(self.id, title)

    async def set_description(self, description: str) -> bool:
        return await self.bot.set_chat_description(self.id, description)

    async def pin_message(self, message_id: int) -> bool:
        return await self.bot.pin_chat_message(self.id, message_id)

    async def unpin_message(self, message_id: int) -> bool:
        return await self.bot.unpin_chat_message(self.id, message_id)

    async def unpin_all_messages(self) -> bool:
        return await self.bot.unpin_all_chat_messages(self.id)


class ChatFullInfo(Chat):
    """Full information about a chat (returned by ``getChat``)."""

    photo: Optional[ChatPhoto] = None
    bio: Optional[str] = None
    description: Optional[str] = None
    invite_link: Optional[str] = None
    linked_chat_id: Optional[str] = None


class ChatMember(BaleObject):
    """Base class for the four chat-member variants."""

    status: str
    user: User


class ChatMemberOwner(ChatMember):
    status: str = "creator"


class ChatMemberAdministrator(ChatMember):
    status: str = "administrator"
    can_delete_messages: Optional[bool] = None
    can_manage_video_chats: Optional[bool] = None
    can_restrict_members: Optional[bool] = None
    can_promote_members: Optional[bool] = None
    can_change_info: Optional[bool] = None
    can_invite_users: Optional[bool] = None
    can_post_stories: Optional[bool] = None
    can_post_messages: Optional[bool] = None
    can_edit_messages: Optional[bool] = None
    can_pin_messages: Optional[bool] = None


class ChatMemberMember(ChatMember):
    status: str = "member"


class ChatMemberRestricted(ChatMember):
    status: str = "restricted"
    is_member: Optional[bool] = None
    can_send_messages: Optional[bool] = None
    can_send_audios: Optional[bool] = None
    can_send_documents: Optional[bool] = None
    can_send_photos: Optional[bool] = None
    can_send_videos: Optional[bool] = None
    can_change_info: Optional[bool] = None
    can_invite_users: Optional[bool] = None
    can_pin_messages: Optional[bool] = None


#: union used when parsing ``getChatMember`` results
AnyChatMember = Union[
    ChatMemberOwner,
    ChatMemberAdministrator,
    ChatMemberRestricted,
    ChatMemberMember,
]

_MEMBER_BY_STATUS = {
    "creator": ChatMemberOwner,
    "administrator": ChatMemberAdministrator,
    "restricted": ChatMemberRestricted,
    "member": ChatMemberMember,
}


def parse_chat_member(data: dict[str, Any]) -> ChatMember:
    """Instantiate the concrete ChatMember subclass for ``data``."""
    cls = _MEMBER_BY_STATUS.get(data.get("status", ""), ChatMember)
    return cls.model_validate(data)
