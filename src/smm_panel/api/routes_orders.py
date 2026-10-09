"""Orders placement and lifecycle management routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from smm_panel.models.order import (
    Order,
    OrderCreate,
    OrderUpdate,
    OrderStatus,
)
from smm_panel.database.repository import SmmRepository
from smm_panel.providers.base import BaseProviderClient
from smm_panel.api.dependencies import get_repo, get_provider_driver

router = APIRouter(prefix="/api/orders", tags=["Orders Management"])


@router.post("", response_model=Order, status_code=201)
async def place_order(
    payload: OrderCreate,
    repo: SmmRepository = Depends(get_repo),
    provider_driver: BaseProviderClient = Depends(get_provider_driver),
):
    """Place new SMM order: validates balance, applies user/promo discounts, deducts balance, and dispatches to provider."""
    try:
        return await repo.place_order(payload, provider_driver=provider_driver)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[Order])
async def list_orders(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    service_id: Optional[int] = Query(None, description="Filter by service ID"),
    repo: SmmRepository = Depends(get_repo),
):
    return await repo.get_orders(user_id=user_id, status=status, service_id=service_id)


@router.get("/{order_id}", response_model=Order)
async def get_order(order_id: int, repo: SmmRepository = Depends(get_repo)):
    order = await repo.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.patch("/{order_id}", response_model=Order)
async def update_order_status(
    order_id: int, payload: OrderUpdate, repo: SmmRepository = Depends(get_repo)
):
    """Update order status. Automatic refunds are issued if marked cancelled or partial."""
    updated = await repo.update_order_status(order_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated
