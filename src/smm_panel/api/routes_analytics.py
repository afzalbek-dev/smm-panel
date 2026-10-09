"""Executive Analytics and Business Dashboard API routes."""

from fastapi import APIRouter, Depends
from smm_panel.models.analytics import SmmDashboardMetrics
from smm_panel.database.repository import SmmRepository
from smm_panel.api.dependencies import get_repo

router = APIRouter(prefix="/api/analytics", tags=["Executive Analytics"])


@router.get("/dashboard", response_model=SmmDashboardMetrics)
async def get_dashboard_metrics(repo: SmmRepository = Depends(get_repo)):
    """Return platform KPI metrics: orders, gross profit, revenue, and platform volume."""
    return await repo.get_dashboard_metrics()
