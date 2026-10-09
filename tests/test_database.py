"""Tests for database repository operations and financial balance ledger."""

import pytest
from smm_panel.database.repository import SmmRepository
from smm_panel.models.user import UserCreate, UserRole, TransactionType
from smm_panel.models.service import ServiceCreate, Platform, ServiceType
from smm_panel.models.order import OrderCreate, OrderUpdate, OrderStatus
from smm_panel.models.promo import PromoCodeCreate
from smm_panel.providers.mock_provider import MockProviderClient


@pytest.mark.asyncio
async def test_initial_seeding(test_repo: SmmRepository):
    """Initial init_db seeds default users, providers, and services."""
    users = await test_repo.get_users()
    assert len(users) >= 2  # Admin and reseller
    assert any(u.role == UserRole.ADMIN for u in users)

    services = await test_repo.get_services()
    assert len(services) >= 6

    providers = await test_repo.get_providers()
    assert len(providers) >= 1


@pytest.mark.asyncio
async def test_user_balance_adjustment(test_repo: SmmRepository):
    """Balance deposits and deductions correctly update balance and create transactions."""
    user = await test_repo.create_user(
        UserCreate(username="trader1", email="trader1@test.com", balance_usd=50.0)
    )
    assert user.balance_usd == 50.0

    # Add funds
    updated = await test_repo.adjust_user_balance(
        user.id, 25.0, TransactionType.DEPOSIT, "Card deposit"
    )
    assert updated.balance_usd == 75.0

    # Check transactions
    txs = await test_repo.get_transactions(user_id=user.id)
    assert len(txs) >= 2
    assert txs[0].amount_usd == 25.0
    assert txs[0].balance_after == 75.0


@pytest.mark.asyncio
async def test_insufficient_balance_error(test_repo: SmmRepository):
    """Negative balance adjustment beyond available funds raises ValueError."""
    user = await test_repo.create_user(
        UserCreate(username="broke_user", email="broke@test.com", balance_usd=10.0)
    )

    with pytest.raises(ValueError, match="Insufficient balance"):
        await test_repo.adjust_user_balance(
            user.id, -15.0, TransactionType.ORDER_CHARGE, "Overdraft attempt"
        )


@pytest.mark.asyncio
async def test_order_placement_and_cancellation_refund(test_repo: SmmRepository):
    """Placing order deducts funds; cancelling order refunds funds."""
    driver = MockProviderClient()
    user = await test_repo.create_user(
        UserCreate(username="order_tester", email="tester@test.com", balance_usd=100.0)
    )
    service = (await test_repo.get_services())[0]

    # Place order for 1,000 units
    order = await test_repo.place_order(
        OrderCreate(
            user_id=user.id,
            service_id=service.id,
            link="https://t.me/testchannel",
            quantity=1000,
        ),
        provider_driver=driver,
    )
    assert order.charge_usd == service.rate_per_1k
    assert order.status == OrderStatus.IN_PROGRESS

    # User balance was deducted
    u_after = await test_repo.get_user_by_id(user.id)
    assert u_after.balance_usd == round(100.0 - order.charge_usd, 4)

    # Cancel order -> automatic full refund
    await test_repo.update_order_status(order.id, OrderUpdate(status=OrderStatus.CANCELLED))

    u_refunded = await test_repo.get_user_by_id(user.id)
    assert u_refunded.balance_usd == 100.0


@pytest.mark.asyncio
async def test_promo_code_validation_and_exhaustion(test_repo: SmmRepository):
    """Promo code validation, discount verification, and max usage limit."""
    promo = await test_repo.create_promo_code(
        PromoCodeCreate(code="FLASH50", discount_percent=50.0, max_uses=2)
    )
    assert promo.code == "FLASH50"

    # Use once
    res1 = await test_repo.validate_and_apply_promo("flash50")
    assert res1.valid is True
    assert res1.discount_percent == 50.0

    # Use twice
    res2 = await test_repo.validate_and_apply_promo("FLASH50")
    assert res2.valid is True

    # Third use should be exhausted
    res3 = await test_repo.validate_and_apply_promo("FLASH50")
    assert res3.valid is False
    assert "limit" in res3.message
