"""FastAPI application factory for SMM Panel Platform."""

from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from smm_panel.config import Settings, get_settings
from smm_panel.database.repository import SmmRepository
from smm_panel.providers.base import BaseProviderClient
from smm_panel.providers.mock_provider import MockProviderClient
from smm_panel.providers.standard_smm import StandardSmmClient
from smm_panel.api import (
    users_router,
    services_router,
    orders_router,
    providers_router,
    reseller_v2_router,
    promos_router,
    analytics_router,
)


def create_app(
    settings: Optional[Settings] = None,
    repo: Optional[SmmRepository] = None,
    provider_driver: Optional[BaseProviderClient] = None,
) -> FastAPI:
    """Create and configure SMM Panel FastAPI application."""
    app_settings = settings or get_settings()
    app_repo = repo or SmmRepository(app_settings.sqlite_path)

    if provider_driver:
        app_driver = provider_driver
    elif app_settings.use_mock_provider:
        app_driver = MockProviderClient()
    else:
        app_driver = StandardSmmClient()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await app_repo.init_db()
        yield

    app = FastAPI(
        title="SMM Panel Aggregator API",
        description="High-concurrency Social Media Marketing reseller aggregator, balance ledger, and order execution platform",
        version="1.0.0",
        lifespan=lifespan,
    )

    # State injection
    app.state.settings = app_settings
    app.state.repo = app_repo
    app.state.provider_driver = app_driver

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount routers
    app.include_router(users_router)
    app.include_router(services_router)
    app.include_router(orders_router)
    app.include_router(providers_router)
    app.include_router(reseller_v2_router)
    app.include_router(promos_router)
    app.include_router(analytics_router)

    @app.get("/", tags=["Health"])
    async def root():
        return {
            "name": "SMM Panel Aggregator",
            "version": "1.0.0",
            "status": "online",
            "environment": app_settings.app_env,
        }

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "service": "smm-panel",
            "database": "connected",
            "environment": app_settings.app_env,
        }

    return app
