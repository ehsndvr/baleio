from __future__ import annotations

from typing import Optional

from pydantic import AliasChoices, Field

from .base import BaleObject
from .user import User


class LabeledPrice(BaleObject):
    """One line item of an invoice. ``amount`` is in Rials (IRR)."""

    label: str
    amount: int


class SuccessfulPayment(BaleObject):
    currency: Optional[str] = None
    total_amount: int
    invoice_payload: Optional[str] = None
    telegram_payment_charge_id: Optional[str] = None
    provider_payment_charge_id: Optional[str] = None


class PreCheckoutQuery(BaleObject):
    """Sent before a wallet payment is finalized; answer within 10 seconds."""

    id: str
    from_user: Optional[User] = Field(
        default=None, validation_alias=AliasChoices("from_user", "from")
    )
    currency: Optional[str] = None
    total_amount: int
    invoice_payload: Optional[str] = None

    async def answer(
        self, ok: bool, error_message: Optional[str] = None
    ) -> bool:
        return await self.bot.answer_pre_checkout_query(
            self.id, ok=ok, error_message=error_message
        )


class Transaction(BaleObject):
    id: str
    status: Optional[str] = None
    userID: Optional[int] = None
    amount: Optional[int] = None
    createdAt: Optional[int] = None
