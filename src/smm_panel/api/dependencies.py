"""FastAPI dependencies for SMM Panel."""

from fastapi import Request
from smm_panel.config import Settings
from smm_panel.database.repository import SmmRepository
from smm_panel.providers.base import BaseProviderClient


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_repo(request: Request) -> SmmRepository:
    return request.app.state.repo


def get_provider_driver(request: Request) -> BaseProviderClient:
    return request.app.state.provider_driver
