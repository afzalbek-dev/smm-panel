"""Configuration management for SMM Panel using Pydantic."""

import os
from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings with environment variable fallbacks."""

    app_name: str = Field(default_factory=lambda: os.getenv("APP_NAME", "smm-panel"))
    app_env: str = Field(default_factory=lambda: os.getenv("APP_ENV", "production"))
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "false").lower() in ("true", "1", "yes"))
    host: str = Field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    database_url: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./smm_panel.db"))
    secret_key: str = Field(
        default_factory=lambda: os.getenv("SECRET_KEY", "smm_panel_super_secret_jwt_key_change_in_production")
    )
    admin_api_key: str = Field(
        default_factory=lambda: os.getenv("ADMIN_API_KEY", "adm_secret_key_smm_panel_2026")
    )

    # SMM Provider settings
    default_provider_url: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_PROVIDER_URL", "https://mock-provider.smm.internal/api/v2")
    )
    default_provider_key: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_PROVIDER_KEY", "mock_provider_key")
    )
    use_mock_provider: bool = Field(
        default_factory=lambda: os.getenv("USE_MOCK_PROVIDER", "true").lower() in ("true", "1", "yes")
    )
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    @property
    def sqlite_path(self) -> Path:
        """Resolve filesystem path for SQLite database."""
        url = self.database_url
        if url.startswith("sqlite:///"):
            path_str = url.replace("sqlite:///", "")
            return Path(path_str).resolve()
        return Path("smm_panel.db").resolve()


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
