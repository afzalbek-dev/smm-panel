"""Services catalog API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from smm_panel.models.service import (
    Service,
    ServiceCreate,
    Platform,
)
from smm_panel.database.repository import SmmRepository
from smm_panel.api.dependencies import get_repo

router = APIRouter(prefix="/api/services", tags=["Services Catalog"])


@router.post("", response_model=Service, status_code=201)
async def create_service(payload: ServiceCreate, repo: SmmRepository = Depends(get_repo)):
    return await repo.create_service(payload)


@router.get("", response_model=List[Service])
async def list_services(
    platform: Optional[Platform] = Query(None, description="Filter by social media platform"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    repo: SmmRepository = Depends(get_repo),
):
    return await repo.get_services(platform=platform, is_active=is_active)


@router.get("/{service_id}", response_model=Service)
async def get_service(service_id: int, repo: SmmRepository = Depends(get_repo)):
    service = await repo.get_service_by_id(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service
