"""SMM API Provider models."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ProviderStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class ProviderCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    api_url: str = Field(min_length=5, max_length=255)
    api_key: str = Field(min_length=1, max_length=255)
    is_active: bool = True


class ProviderUpdate(BaseModel):
    name: Optional[str] = None
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    is_active: Optional[bool] = None


class Provider(BaseModel):
    id: int
    name: str
    api_url: str
    api_key: str
    balance_usd: float = 0.0
    currency: str = "USD"
    is_active: bool = True
    last_sync_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=utc_now)


class ProviderBalance(BaseModel):
    provider_id: int
    balance: float
    currency: str = "USD"
