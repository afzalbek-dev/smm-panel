"""Live Standard SMM API v2 Client implementation using httpx."""

import logging
from typing import Dict, Any, List, Optional
import httpx

from smm_panel.providers.base import BaseProviderClient

logger = logging.getLogger(__name__)


class StandardSmmClient(BaseProviderClient):
    """Production HTTP client conforming to Standard SMM v2 API Protocol."""

    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout

    async def get_balance(self, api_url: str, api_key: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(api_url, data={"key": api_key, "action": "balance"})
            resp.raise_for_status()
            data = resp.json()
            balance_val = float(data.get("balance", 0.0))
            return {"balance": balance_val, "currency": data.get("currency", "USD")}

    async def place_order(
        self,
        api_url: str,
        api_key: str,
        service_id: int,
        link: str,
        quantity: int,
        comments: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "key": api_key,
            "action": "add",
            "service": service_id,
            "link": link,
            "quantity": quantity,
        }
        if comments:
            payload["comments"] = comments

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(api_url, data=payload)
            resp.raise_for_status()
            data = resp.json()
            if "error" in data:
                raise ValueError(f"Upstream provider error: {data['error']}")
            return data

    async def get_order_status(
        self, api_url: str, api_key: str, provider_order_id: str
    ) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                api_url, data={"key": api_key, "action": "status", "order": provider_order_id}
            )
            resp.raise_for_status()
            return resp.json()

    async def fetch_services(self, api_url: str, api_key: str) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(api_url, data={"key": api_key, "action": "services"})
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list):
                return data
            return []
