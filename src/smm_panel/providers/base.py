"""Abstract interface for SMM API Providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseProviderClient(ABC):
    """Abstract driver interface for interacting with upstream SMM Providers."""

    @abstractmethod
    async def get_balance(self, api_url: str, api_key: str) -> Dict[str, Any]:
        """Fetch upstream provider balance and currency."""
        pass

    @abstractmethod
    async def place_order(
        self,
        api_url: str,
        api_key: str,
        service_id: int,
        link: str,
        quantity: int,
        comments: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Forward order to upstream SMM provider. Returns dict with 'order' ID."""
        pass

    @abstractmethod
    async def get_order_status(
        self, api_url: str, api_key: str, provider_order_id: str
    ) -> Dict[str, Any]:
        """Query status of single order from upstream provider."""
        pass

    @abstractmethod
    async def fetch_services(self, api_url: str, api_key: str) -> List[Dict[str, Any]]:
        """Fetch list of available services from upstream provider."""
        pass
