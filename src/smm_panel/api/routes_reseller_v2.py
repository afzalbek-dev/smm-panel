"""Standard SMM API v2 protocol endpoint for reseller platforms."""

from typing import Union, Dict, Any, List
from fastapi import APIRouter, Depends, Request, Form
from smm_panel.models.order import OrderCreate, OrderStatus
from smm_panel.database.repository import SmmRepository
from smm_panel.providers.base import BaseProviderClient
from smm_panel.api.dependencies import get_repo, get_provider_driver

router = APIRouter(prefix="/api/v2", tags=["Standard SMM v2 Reseller Protocol"])


@router.post("")
async def handle_v2_request(
    request: Request,
    repo: SmmRepository = Depends(get_repo),
    driver: BaseProviderClient = Depends(get_provider_driver),
) -> Any:
    """Standard SMM API v2 multi-action dispatcher."""
    # Parse either form-encoded body or JSON body
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
        except Exception:
            body = {}
    else:
        form = await request.form()
        body = dict(form)

    api_key = body.get("key")
    if not api_key:
        return {"error": "Missing API key"}

    user = await repo.get_user_by_api_key(str(api_key))
    if not user or not user.is_active:
        return {"error": "Invalid or inactive API key"}

    action = body.get("action")
    if not action:
        return {"error": "Missing action parameter"}

    # 1. Action: balance
    if action == "balance":
        return {
            "balance": f"{user.balance_usd:.2f}",
            "currency": "USD",
        }

    # 2. Action: services
    elif action == "services":
        services = await repo.get_services(is_active=True)
        return [
            {
                "service": s.id,
                "name": s.name,
                "type": "Default",
                "category": s.category,
                "rate": f"{s.rate_per_1k:.2f}",
                "min": str(s.min_quantity),
                "max": str(s.max_quantity),
                "refill": s.refill_supported,
            }
            for s in services
        ]

    # 3. Action: add (Place order)
    elif action == "add":
        service_id = body.get("service")
        link = body.get("link")
        quantity = body.get("quantity")

        if not service_id or not link or not quantity:
            return {"error": "Missing service, link, or quantity"}

        try:
            sid_int = int(service_id)
            qty_int = int(quantity)
        except ValueError:
            return {"error": "Service ID and quantity must be valid integers"}

        try:
            order = await repo.place_order(
                OrderCreate(
                    user_id=user.id,
                    service_id=sid_int,
                    link=str(link),
                    quantity=qty_int,
                    comments=body.get("comments", ""),
                ),
                provider_driver=driver,
            )
            return {"order": order.id}
        except ValueError as e:
            return {"error": str(e)}

    # 4. Action: status
    elif action == "status":
        order_id = body.get("order")
        orders_param = body.get("orders")

        if order_id:
            try:
                oid = int(order_id)
            except ValueError:
                return {"error": "Incorrect order ID"}
            ord_obj = await repo.get_order_by_id(oid)
            if not ord_obj or ord_obj.user_id != user.id:
                return {"error": "Order not found"}

            return {
                "charge": f"{ord_obj.charge_usd:.4f}",
                "start_count": str(ord_obj.start_count),
                "status": ord_obj.status.value.replace("_", " ").title(),
                "remains": str(ord_obj.remains),
                "currency": "USD",
            }

        elif orders_param:
            # Multi-order status check
            raw_ids = [s.strip() for s in str(orders_param).split(",") if s.strip()]
            results: Dict[str, Any] = {}
            for raw in raw_ids:
                try:
                    oid = int(raw)
                    ord_obj = await repo.get_order_by_id(oid)
                    if ord_obj and ord_obj.user_id == user.id:
                        results[str(oid)] = {
                            "charge": f"{ord_obj.charge_usd:.4f}",
                            "start_count": str(ord_obj.start_count),
                            "status": ord_obj.status.value.replace("_", " ").title(),
                            "remains": str(ord_obj.remains),
                            "currency": "USD",
                        }
                    else:
                        results[str(oid)] = {"error": "Order not found"}
                except ValueError:
                    results[raw] = {"error": "Incorrect order ID"}
            return results

        return {"error": "Missing order or orders parameter"}

    return {"error": f"Unknown action '{action}'"}
