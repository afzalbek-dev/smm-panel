"""User and Financial Account models."""

import secrets
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_api_key() -> str:
    return f"smm_{secrets.token_hex(16)}"


class UserRole(str, Enum):
    ADMIN = "admin"
    RESELLER = "reseller"
    USER = "user"


class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    ORDER_CHARGE = "order_charge"
    REFUND = "refund"
    BONUS = "bonus"


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=5, max_length=120)
    role: UserRole = UserRole.USER
    balance_usd: float = Field(default=0.0, ge=0.0)
    discount_percent: float = Field(default=0.0, ge=0.0, le=90.0)


class UserUpdate(BaseModel):
    email: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    discount_percent: Optional[float] = None


class User(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole = UserRole.USER
    balance_usd: float = 0.0
    discount_percent: float = 0.0
    api_key: str = Field(default_factory=generate_api_key)
    is_active: bool = True
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class BalanceDeposit(BaseModel):
    amount_usd: float = Field(gt=0.0, le=100000.0)
    note: Optional[str] = "Manual Balance Credit"


class Transaction(BaseModel):
    id: int
    user_id: int
    type: TransactionType
    amount_usd: float
    balance_after: float
    description: str = ""
    created_at: datetime = Field(default_factory=utc_now)
