"""Tests for Services catalog API endpoints."""

from starlette.testclient import TestClient


def test_list_and_filter_services(client: TestClient):
    """GET /api/services returns catalog and filters by platform."""
    res = client.get("/api/services")
    assert res.status_code == 200
    services = res.json()
    assert len(services) >= 6

    # Filter by platform
    tg_res = client.get("/api/services?platform=telegram")
    assert tg_res.status_code == 200
    tg_services = tg_res.json()
    assert all(s["platform"] == "telegram" for s in tg_services)


def test_create_and_get_service(client: TestClient):
    """POST /api/services creates new service item."""
    payload = {
        "name": "X / Twitter Organic Retweets",
        "platform": "twitter",
        "service_type": "shares",
        "category": "Twitter Engagement",
        "rate_per_1k": 3.20,
        "min_quantity": 25,
        "max_quantity": 10000,
        "refill_supported": True,
        "description": "High retention retweets",
    }
    res = client.post("/api/services", json=payload)
    assert res.status_code == 201
    created = res.json()
    assert created["name"] == "X / Twitter Organic Retweets"
    assert created["rate_per_1k"] == 3.20
    sid = created["id"]

    # Get by ID
    get_res = client.get(f"/api/services/{sid}")
    assert get_res.status_code == 200
    assert get_res.json()["platform"] == "twitter"
