"""Tests for Standard SMM v2 Reseller Protocol API routes."""

from starlette.testclient import TestClient


def test_v2_balance_action(client: TestClient):
    """POST /api/v2 with action=balance returns formatted balance."""
    # Find reseller_pro
    users = client.get("/api/users").json()
    reseller = next(u for u in users if u["username"] == "reseller_pro")
    api_key = reseller["api_key"]

    res = client.post("/api/v2", json={"key": api_key, "action": "balance"})
    assert res.status_code == 200
    data = res.json()
    assert "balance" in data
    assert data["currency"] == "USD"
    assert float(data["balance"]) == 150.0


def test_v2_services_action(client: TestClient):
    """POST /api/v2 with action=services returns standard services array."""
    reseller = next(u for u in client.get("/api/users").json() if u["username"] == "reseller_pro")
    api_key = reseller["api_key"]

    res = client.post("/api/v2", json={"key": api_key, "action": "services"})
    assert res.status_code == 200
    services = res.json()
    assert isinstance(services, list)
    assert len(services) >= 6
    assert "service" in services[0]
    assert "rate" in services[0]
    assert "min" in services[0]
    assert "max" in services[0]


def test_v2_add_and_status_action(client: TestClient):
    """POST /api/v2 action=add creates order and action=status checks progress."""
    reseller = next(u for u in client.get("/api/users").json() if u["username"] == "reseller_pro")
    api_key = reseller["api_key"]
    services = client.get("/api/services").json()
    service_id = services[0]["id"]

    # 1. Add order
    add_res = client.post(
        "/api/v2",
        json={
            "key": api_key,
            "action": "add",
            "service": service_id,
            "link": "https://instagram.com/viral_post",
            "quantity": 100,
        },
    )
    assert add_res.status_code == 200
    add_data = add_res.json()
    assert "order" in add_data
    order_id = add_data["order"]

    # 2. Check single status
    status_res = client.post(
        "/api/v2",
        json={"key": api_key, "action": "status", "order": order_id},
    )
    assert status_res.status_code == 200
    s_data = status_res.json()
    assert "status" in s_data
    assert "charge" in s_data
    assert "remains" in s_data

    # 3. Check multi status
    multi_res = client.post(
        "/api/v2",
        json={"key": api_key, "action": "status", "orders": f"{order_id},999999"},
    )
    assert multi_res.status_code == 200
    m_data = multi_res.json()
    assert str(order_id) in m_data
    assert "999999" in m_data
    assert "error" in m_data["999999"]


def test_v2_auth_errors(client: TestClient):
    """Missing or invalid API key returns descriptive JSON error."""
    assert client.post("/api/v2", json={"action": "balance"}).json() == {"error": "Missing API key"}
    assert client.post("/api/v2", json={"key": "invalid_key", "action": "balance"}).json() == {
        "error": "Invalid or inactive API key"
    }
