"""User accounts, balance, and transaction ledger API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from smm_panel.models.user import (
    User,
    UserCreate,
    BalanceDeposit,
    Transaction,
    TransactionType,
)
from smm_panel.database.repository import SmmRepository
from smm_panel.api.dependencies import get_repo

router = APIRouter(prefix="/api/users", tags=["Users & Balances"])


@router.post("", response_model=User, status_code=201)
async def create_user(payload: UserCreate, repo: SmmRepository = Depends(get_repo)):
    return await repo.create_user(payload)


@router.get("", response_model=List[User])
async def list_users(repo: SmmRepository = Depends(get_repo)):
    return await repo.get_users()


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int, repo: SmmRepository = Depends(get_repo)):
    user = await repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/{user_id}/deposit", response_model=User)
async def deposit_balance(
    user_id: int, payload: BalanceDeposit, repo: SmmRepository = Depends(get_repo)
):
    """Credit funds to user account balance and record in financial ledger."""
    try:
        return await repo.adjust_user_balance(
            user_id=user_id,
            amount=payload.amount_usd,
            tx_type=TransactionType.DEPOSIT,
            description=payload.note or "Balance top-up",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}/transactions", response_model=List[Transaction])
async def list_user_transactions(user_id: int, repo: SmmRepository = Depends(get_repo)):
    user = await repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await repo.get_transactions(user_id=user_id)
