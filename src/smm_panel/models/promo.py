"""Promo code and marketing models."""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PromoCodeCreate(BaseModel):
    code: str = Field(min_length=3, max_length=30)
    discount_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    bonus_usd: float = Field(default=0.0, ge=0.0)
    max_uses: int = Field(default=100, ge=1)


class PromoCode(BaseModel):
    id: int
    code: str
    discount_percent: float = 0.0
    bonus_usd: float = 0.0
    max_uses: int = 100
    times_used: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=utc_now)


class PromoApplyResult(BaseModel):
    valid: bool
    discount_percent: float = 0.0
    bonus_usd: float = 0.0
    message: str
