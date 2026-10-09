"""Tests for User API endpoints."""

from starlette.testclient import TestClient


def test_create_and_list_users(client: TestClient):
    """POST /api/users creates user, GET lists users."""
    payload = {
        "username": "reseller_john",
        "email": "john@smmagency.com",
        "role": "reseller",
        "balance_usd": 250.0,
        "discount_percent": 10.0,
    }
    res = client.post("/api/users", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["username"] == "reseller_john"
    assert data["balance_usd"] == 250.0
    assert "api_key" in data

    # List users
    list_res = client.get("/api/users")
    assert list_res.status_code == 200
    assert any(u["username"] == "reseller_john" for u in list_res.json())


def test_deposit_balance_and_transactions(client: TestClient):
    """POST /api/users/{id}/deposit credits user balance and creates ledger transaction."""
    user = client.post(
        "/api/users",
        json={"username": "alice", "email": "alice@gmail.com", "balance_usd": 0.0},
    ).json()
    uid = user["id"]

    dep_res = client.post(
        f"/api/users/{uid}/deposit",
        json={"amount_usd": 150.0, "note": "Crypto deposit TRX"},
    )
    assert dep_res.status_code == 200
    assert dep_res.json()["balance_usd"] == 150.0

    # View transactions
    tx_res = client.get(f"/api/users/{uid}/transactions")
    assert tx_res.status_code == 200
    txs = tx_res.json()
    assert len(txs) >= 1
    assert txs[0]["amount_usd"] == 150.0
    assert "Crypto" in txs[0]["description"]


def test_user_not_found(client: TestClient):
    """404 returned for missing user."""
    assert client.get("/api/users/999999").status_code == 404
    assert client.post("/api/users/999999/deposit", json={"amount_usd": 10.0}).status_code == 400
