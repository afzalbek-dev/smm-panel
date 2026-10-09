"""SMM Panel API package."""

from smm_panel.api.routes_users import router as users_router
from smm_panel.api.routes_services import router as services_router
from smm_panel.api.routes_orders import router as orders_router
from smm_panel.api.routes_providers import router as providers_router
from smm_panel.api.routes_reseller_v2 import router as reseller_v2_router
from smm_panel.api.routes_promos import router as promos_router
from smm_panel.api.routes_analytics import router as analytics_router

__all__ = [
    "users_router",
    "services_router",
    "orders_router",
    "providers_router",
    "reseller_v2_router",
    "promos_router",
    "analytics_router",
]
