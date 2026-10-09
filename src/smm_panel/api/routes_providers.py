"""Upstream SMM Provider management routes."""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from smm_panel.models.provider import (
    Provider,
    ProviderCreate,
    ProviderBalance,
)
from smm_panel.database.repository import SmmRepository
from smm_panel.providers.base import BaseProviderClient
from smm_panel.api.dependencies import get_repo, get_provider_driver

router = APIRouter(prefix="/api/providers", tags=["Providers & Upstream APIs"])


@router.post("", response_model=Provider, status_code=201)
async def create_provider(payload: ProviderCreate, repo: SmmRepository = Depends(get_repo)):
    return await repo.create_provider(payload)


@router.get("", response_model=List[Provider])
async def list_providers(repo: SmmRepository = Depends(get_repo)):
    return await repo.get_providers()


@router.get("/{provider_id}", response_model=Provider)
async def get_provider(provider_id: int, repo: SmmRepository = Depends(get_repo)):
    provider = await repo.get_provider_by_id(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.get("/{provider_id}/balance", response_model=ProviderBalance)
async def check_provider_balance(
    provider_id: int,
    repo: SmmRepository = Depends(get_repo),
    driver: BaseProviderClient = Depends(get_provider_driver),
):
    """Query live balance from upstream provider API and synchronize database record."""
    provider = await repo.get_provider_by_id(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    try:
        res = await driver.get_balance(provider.api_url, provider.api_key)
        new_balance = float(res.get("balance", 0.0))
        await repo.update_provider_balance(provider_id, new_balance)
        return ProviderBalance(
            provider_id=provider_id,
            balance=new_balance,
            currency=res.get("currency", "USD"),
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to query provider balance: {e}")


@router.get("/{provider_id}/services")
async def fetch_upstream_services(
    provider_id: int,
    repo: SmmRepository = Depends(get_repo),
    driver: BaseProviderClient = Depends(get_provider_driver),
) -> List[Dict[str, Any]]:
    """Fetch external services catalog directly from provider API."""
    provider = await repo.get_provider_by_id(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    try:
        return await driver.fetch_services(provider.api_url, provider.api_key)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch upstream services: {e}")
