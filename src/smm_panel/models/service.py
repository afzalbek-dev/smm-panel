"""SMM Services and Catalog models."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Platform(str, Enum):
    TELEGRAM = "telegram"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    OTHER = "other"


class ServiceType(str, Enum):
    FOLLOWERS = "followers"
    LIKES = "likes"
    VIEWS = "views"
    COMMENTS = "comments"
    SHARES = "shares"
    CUSTOM = "custom"


class ServiceCreate(BaseModel):
    name: str = Field(min_length=3, max_length=150)
    platform: Platform = Platform.TELEGRAM
    service_type: ServiceType = ServiceType.FOLLOWERS
    category: str = Field(default="Telegram Services", max_length=100)
    rate_per_1k: float = Field(gt=0.0, description="Retail price per 1000 units in USD")
    min_quantity: int = Field(default=10, ge=1)
    max_quantity: int = Field(default=100000, ge=10)
    provider_id: Optional[int] = None
    provider_service_id: Optional[int] = None
    provider_rate_per_1k: Optional[float] = 0.0
    refill_supported: bool = True
    description: Optional[str] = ""


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    platform: Optional[Platform] = None
    service_type: Optional[ServiceType] = None
    category: Optional[str] = None
    rate_per_1k: Optional[float] = None
    min_quantity: Optional[int] = None
    max_quantity: Optional[int] = None
    provider_id: Optional[int] = None
    provider_service_id: Optional[int] = None
    provider_rate_per_1k: Optional[float] = None
    is_active: Optional[bool] = None
    refill_supported: Optional[bool] = None
    description: Optional[str] = None


class Service(BaseModel):
    id: int
    name: str
    platform: Platform
    service_type: ServiceType
    category: str
    rate_per_1k: float
    min_quantity: int
    max_quantity: int
    provider_id: Optional[int] = None
    provider_service_id: Optional[int] = None
    provider_rate_per_1k: float = 0.0
    is_active: bool = True
    refill_supported: bool = True
    description: str = ""
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
