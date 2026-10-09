"""Deterministic Mock SMM Provider Client for zero-secret environments and tests."""

import logging
from typing import Dict, Any, List, Optional
from smm_panel.providers.base import BaseProviderClient

logger = logging.getLogger(__name__)


class MockProviderClient(BaseProviderClient):
    """Deterministic in-memory mock client implementing Standard SMM v2 protocol."""

    def __init__(self, initial_balance: float = 2500.0):
        self._balance = initial_balance
        self._orders_db: Dict[str, Dict[str, Any]] = {}
        self._order_counter = 50000

    async def get_balance(self, api_url: str, api_key: str) -> Dict[str, Any]:
        return {"balance": round(self._balance, 2), "currency": "USD"}

    async def place_order(
        self,
        api_url: str,
        api_key: str,
        service_id: int,
        link: str,
        quantity: int,
        comments: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._order_counter += 1
        prov_id = str(self._order_counter)

        # Provider charge approx $0.30 per 1k for mock
        est_charge = round((quantity / 1000.0) * 0.30, 4)
        self._balance = max(0.0, self._balance - est_charge)

        self._orders_db[prov_id] = {
            "order": prov_id,
            "charge": str(est_charge),
            "start_count": "1200",
            "status": "In progress",
            "remains": str(quantity),
            "currency": "USD",
        }
        logger.info(f"MockProvider placed order {prov_id} for service {service_id}")
        return {"order": int(prov_id)}

    async def get_order_status(
        self, api_url: str, api_key: str, provider_order_id: str
    ) -> Dict[str, Any]:
        str_id = str(provider_order_id)
        if str_id in self._orders_db:
            ord_info = self._orders_db[str_id]
            # Advance to completed on check
            ord_info["status"] = "Completed"
            ord_info["remains"] = "0"
            return ord_info

        return {
            "charge": "0.15",
            "start_count": "500",
            "status": "Completed",
            "remains": "0",
            "currency": "USD",
        }

    async def fetch_services(self, api_url: str, api_key: str) -> List[Dict[str, Any]]:
        return [
            {
                "service": 101,
                "name": "Telegram Channel Members [High Quality]",
                "type": "Default",
                "category": "Telegram",
                "rate": "0.75",
                "min": "100",
                "max": "50000",
                "refill": True,
            },
            {
                "service": 102,
                "name": "Instagram Post Likes [Instant Speed]",
                "type": "Default",
                "category": "Instagram",
                "rate": "0.35",
                "min": "50",
                "max": "20000",
                "refill": False,
            },
            {
                "service": 103,
                "name": "YouTube Video Views [Retention Safe]",
                "type": "Default",
                "category": "YouTube",
                "rate": "1.20",
                "min": "500",
                "max": "100000",
                "refill": True,
            },
        ]
