"""Promo codes and marketing promotions API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from smm_panel.models.promo import PromoCode, PromoCodeCreate, PromoApplyResult
from smm_panel.database.repository import SmmRepository
from smm_panel.api.dependencies import get_repo

router = APIRouter(prefix="/api/promos", tags=["Promotions & Promo Codes"])


class ValidatePromoRequest(BaseModel):
    code: str


@router.post("", response_model=PromoCode, status_code=201)
async def create_promo_code(payload: PromoCodeCreate, repo: SmmRepository = Depends(get_repo)):
    return await repo.create_promo_code(payload)


@router.post("/validate", response_model=PromoApplyResult)
async def validate_promo_code(
    payload: ValidatePromoRequest, repo: SmmRepository = Depends(get_repo)
):
    return await repo.validate_and_apply_promo(payload.code)
