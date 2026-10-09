"""Pytest fixtures for SMM Panel test suite."""

import pytest
from pathlib import Path
from starlette.testclient import TestClient

from smm_panel.config import Settings
from smm_panel.database.repository import SmmRepository
from smm_panel.providers.mock_provider import MockProviderClient
from smm_panel.app import create_app


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    return tmp_path / "test_smm.db"


@pytest.fixture
def test_settings(temp_db_path: Path) -> Settings:
    return Settings(
        database_url=f"sqlite:///{temp_db_path}",
        app_env="testing",
        log_level="DEBUG",
        use_mock_provider=True,
    )


@pytest.fixture
def test_driver() -> MockProviderClient:
    return MockProviderClient(initial_balance=3000.0)


@pytest.fixture
async def test_repo(temp_db_path: Path) -> SmmRepository:
    repo = SmmRepository(temp_db_path)
    await repo.init_db()
    return repo


@pytest.fixture
def test_app(test_settings: Settings, test_repo: SmmRepository, test_driver: MockProviderClient):
    return create_app(
        settings=test_settings,
        repo=test_repo,
        provider_driver=test_driver,
    )


@pytest.fixture
def client(test_app) -> TestClient:
    with TestClient(test_app) as c:
        yield c
