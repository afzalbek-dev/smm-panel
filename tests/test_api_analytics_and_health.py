"""Tests for Analytics dashboard, Providers, Promos, and Health endpoints."""

from starlette.testclient import TestClient


def test_health_and_root(client: TestClient):
    """GET / and /health return healthy status and service info."""
    root_res = client.get("/")
    assert root_res.status_code == 200
    assert root_res.json()["name"] == "SMM Panel Aggregator"

    health_res = client.get("/health")
    assert health_res.status_code == 200
    h_data = health_res.json()
    assert h_data["status"] == "healthy"
    assert h_data["service"] == "smm-panel"
    assert h_data["database"] == "connected"


def test_analytics_dashboard(client: TestClient):
    """GET /api/analytics/dashboard returns full KPI summary."""
    res = client.get("/api/analytics/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "total_orders" in data
    assert "total_users" in data
    assert "total_services" in data
    assert "total_revenue_usd" in data
    assert "gross_profit_usd" in data
    assert "platform_breakdown" in data
    assert isinstance(data["platform_breakdown"], list)


def test_provider_endpoints(client: TestClient):
    """List providers and sync upstream provider balance."""
    providers = client.get("/api/providers").json()
    assert len(providers) >= 1
    pid = providers[0]["id"]

    bal_res = client.get(f"/api/providers/{pid}/balance")
    assert bal_res.status_code == 200
    bal_data = bal_res.json()
    assert "balance" in bal_data
    assert bal_data["currency"] == "USD"


def test_promo_code_validation_endpoint(client: TestClient):
    """POST /api/promos/validate checks code validity."""
    valid_res = client.post("/api/promos/validate", json={"code": "START2026"})
    assert valid_res.status_code == 200
    assert valid_res.json()["valid"] is True
    assert valid_res.json()["discount_percent"] == 10.0

    invalid_res = client.post("/api/promos/validate", json={"code": "NON_EXISTENT"})
    assert invalid_res.status_code == 200
    assert invalid_res.json()["valid"] is False
