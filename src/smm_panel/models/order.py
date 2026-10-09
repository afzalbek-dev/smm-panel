"""SMM Order models and Reseller V2 API contracts."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Union, List
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class OrderCreate(BaseModel):
    user_id: int
    service_id: int
    link: str = Field(min_length=3, max_length=500)
    quantity: int = Field(gt=0)
    comments: Optional[str] = ""
    promo_code: Optional[str] = None


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    start_count: Optional[int] = None
    remains: Optional[int] = None
    provider_order_id: Optional[str] = None


class Order(BaseModel):
    id: int
    user_id: int
    service_id: int
    link: str
    quantity: int
    charge_usd: float
    provider_cost_usd: float = 0.0
    start_count: int = 0
    remains: int = 0
    status: OrderStatus = OrderStatus.PENDING
    provider_id: Optional[int] = None
    provider_order_id: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


# Standard SMM API v2 protocol contracts
class ResellerAddOrderForm(BaseModel):
    key: str
    action: str = "add"
    service: int
    link: str
    quantity: int
    comments: Optional[str] = ""


class ResellerStatusForm(BaseModel):
    key: str
    action: str = "status"
    order: Optional[int] = None
    orders: Optional[str] = None


class ResellerOrderStatusResponse(BaseModel):
    charge: str
    start_count: str
    status: str
    remains: str
    currency: str = "USD"
