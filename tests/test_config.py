"""Tests for SMM Panel configuration."""

from smm_panel.config import Settings, get_settings


def test_settings_defaults():
    s = Settings(database_url="sqlite:///./custom.db")
    assert s.app_name == "smm-panel"
    assert s.port == 8000
    assert s.use_mock_provider is True


def test_sqlite_path_resolution():
    s = Settings(database_url="sqlite:///./data/test.db")
    path = s.sqlite_path
    assert path.name == "test.db"


def test_cached_settings():
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
