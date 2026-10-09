"""Analytics and business reporting models for SMM Panel."""

from typing import List
from pydantic import BaseModel


class PlatformMetric(BaseModel):
    platform: str
    order_count: int
    revenue_usd: float


class SmmDashboardMetrics(BaseModel):
    total_orders: int = 0
    completed_orders: int = 0
    pending_orders: int = 0
    total_revenue_usd: float = 0.0
    total_provider_cost_usd: float = 0.0
    gross_profit_usd: float = 0.0
    profit_margin_percent: float = 0.0
    total_users: int = 0
    total_services: int = 0
    platform_breakdown: List[PlatformMetric] = []
