"""Tests for Orders placement and execution API routes."""

from starlette.testclient import TestClient


def test_order_placement_flow(client: TestClient):
    """Create funded user, place order, inspect order status and user balance."""
    # 1. Create user with $50
    user = client.post(
        "/api/users",
        json={"username": "bob_buyer", "email": "bob@buyer.com", "balance_usd": 50.0},
    ).json()
    uid = user["id"]

    # 2. Get first service
    services = client.get("/api/services").json()
    service = services[0]
    sid = service["id"]

    # 3. Place order for 500 units
    order_payload = {
        "user_id": uid,
        "service_id": sid,
        "link": "https://t.me/example_channel",
        "quantity": 500,
    }
    order_res = client.post("/api/orders", json=order_payload)
    assert order_res.status_code == 201
    ord_data = order_res.json()
    assert ord_data["quantity"] == 500
    assert ord_data["charge_usd"] > 0.0
    assert ord_data["status"] == "in_progress"
    oid = ord_data["id"]

    # 4. Check user balance deducted
    u_updated = client.get(f"/api/users/{uid}").json()
    assert u_updated["balance_usd"] < 50.0

    # 5. Retrieve order details
    get_res = client.get(f"/api/orders/{oid}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == oid


def test_order_insufficient_balance(client: TestClient):
    """400 returned when user has insufficient balance."""
    user = client.post(
        "/api/users",
        json={"username": "zero_bal", "email": "zero@buyer.com", "balance_usd": 0.0},
    ).json()
    services = client.get("/api/services").json()

    res = client.post(
        "/api/orders",
        json={
            "user_id": user["id"],
            "service_id": services[0]["id"],
            "link": "https://t.me/zero",
            "quantity": 1000,
        },
    )
    assert res.status_code == 400
    assert "Insufficient balance" in res.json()["detail"]


def test_order_partial_refund(client: TestClient):
    """Updating order status to partial triggers proportional refund to user balance."""
    user = client.post(
        "/api/users",
        json={"username": "partial_user", "email": "part@buyer.com", "balance_usd": 100.0},
    ).json()
    uid = user["id"]
    service = client.get("/api/services").json()[0]

    # Place order for 1,000 units
    order = client.post(
        "/api/orders",
        json={"user_id": uid, "service_id": service["id"], "link": "https://t.me/part", "quantity": 1000},
    ).json()
    oid = order["id"]
    charge = order["charge_usd"]

    # 500 remains, mark partial
    patch_res = client.patch(
        f"/api/orders/{oid}",
        json={"status": "partial", "remains": 500, "start_count": 100},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "partial"

    # User balance should have been credited approx half the charge
    u_after = client.get(f"/api/users/{uid}").json()
    expected_refund = charge * 0.5
    assert abs(u_after["balance_usd"] - (100.0 - charge + expected_refund)) < 0.05
