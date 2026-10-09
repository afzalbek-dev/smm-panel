# 🚀 SMM Panel — High-Concurrency SMM Reseller Aggregator & Order Execution Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.10+-e92063.svg)](https://docs.pydantic.dev/)
[![SQLite / aiosqlite](https://img.shields.io/badge/Database-aiosqlite-003B57.svg?logo=sqlite&logoColor=white)](https://sqlite.org)
[![Tests Passing](https://img.shields.io/badge/tests-24%2F24%20passed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**SMM Panel** is an enterprise-grade, asynchronous Social Media Marketing reseller aggregator, balance ledger, and automated order execution platform built on Python and FastAPI. It fully implements the industry-standard **Standard SMM API v2 protocol**.

> 🌐 Documentation in other languages: [O'zbekcha (README.md)](README.md) | [Русский (README.ru.md)](README.ru.md)

---

## 🌟 Key Features

- **🔌 Standard SMM API v2 Protocol Implementation:**
  - 100% compatible with reseller platforms like Perfect Panel, JAP, and custom scripts.
  - `action=services`: Retrieve active services, pricing per 1,000, and quantity limits.
  - `action=add`: Validate balance, apply reseller discounts, charge user, and dispatch order.
  - `action=status`: Inspect individual orders or comma-separated batch order IDs.
  - `action=balance`: Query reseller real-time wallet balance.

- **💳 Atomic Balance & Financial Ledger:**
  - Race-condition free balance management with strict overdraft prevention.
  - Full audit trail recording deposits, order charges, full refunds, and partial refunds.

- **🔄 Automatic Refund Management:**
  - Cancelled or refunded orders automatically reverse charges back to customer balance.
  - Partial orders compute unprocessed quantities (`remains`) and issue proportional refunds.

- **🌐 Multi-Provider Architecture & Mock Driver:**
  - Upstream provider registry with balance synchronization and catalog imports.
  - Deterministic in-memory **Mock Provider Driver** for offline environments and CI/CD without API keys.

- **🎁 Promo Codes & Reseller Tiers:**
  - Percentage and fixed bonus promo codes with redemption quotas and expiration controls.
  - Account-level discount percentages (`discount_percent`) for tiered reseller pricing.

- **📈 Executive Analytics Dashboard:**
  - Gross revenue, provider cost, gross profit, profit margin %, total orders, and platform breakdown (Telegram, Instagram, YouTube, TikTok, X).

---

## 🏗 Architecture & Codebase Layout

```
smm-panel/
├── src/smm_panel/
│   ├── api/
│   │   ├── dependencies.py         # FastAPI dependency injection
│   │   ├── routes_users.py         # User management, deposits, and ledger transactions
│   │   ├── routes_services.py      # Catalog endpoints with platform filters
│   │   ├── routes_orders.py        # Order placement, status tracking, and refunds
│   │   ├── routes_providers.py     # Upstream SMM providers & balance sync
│   │   ├── routes_reseller_v2.py   # Standard SMM API v2 protocol dispatcher
│   │   ├── routes_promos.py        # Marketing promo codes validation
│   │   └── routes_analytics.py     # Business KPI dashboard
│   ├── database/
│   │   └── repository.py           # Async SQLite repository layer
│   ├── models/
│   │   ├── user.py                 # Users & transactions schemas
│   │   ├── service.py              # Services & categories schemas
│   │   ├── order.py                # Order lifecycle & SMM v2 protocol schemas
│   │   ├── provider.py             # Provider credentials and sync schemas
│   │   ├── promo.py                # Promo code models
│   │   └── analytics.py            # Dashboard metrics schemas
│   ├── providers/
│   │   ├── base.py                 # Abstract provider driver interface
│   │   ├── standard_smm.py         # Live HTTP provider client (httpx)
│   │   └── mock_provider.py        # Deterministic offline mock driver
│   ├── app.py                      # FastAPI application factory
│   ├── config.py                   # Pydantic configuration settings
│   └── main.py                     # Server launch script
├── tests/
│   ├── conftest.py                 # Pytest fixtures and mock driver
│   ├── test_config.py              # Configuration tests
│   ├── test_database.py            # Database ledger and refund logic tests
│   ├── test_api_users.py           # Users API routes tests
│   ├── test_api_services.py        # Services catalog tests
│   ├── test_api_orders.py          # Order execution & partial refund tests
│   ├── test_api_reseller_v2.py     # SMM v2 reseller protocol tests
│   └── test_api_analytics_and_health.py # Dashboard & health route tests
├── Dockerfile                      # Production container image
├── docker-compose.yml              # Container compose orchestration
├── pyproject.toml                  # Python package metadata
├── requirements.txt                # Dependencies list
└── .env.example                    # Sample environment variables
```

---

## 🚀 Installation & Quick Start

### Prerequisites
- Python 3.11+
- Git

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/afzalbek-dev/smm-panel.git
cd smm-panel

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
```
Key configuration settings:
```env
APP_ENV=production
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./smm_panel.db
USE_MOCK_PROVIDER=true
LOG_LEVEL=INFO
```

### 3. Run Application
```bash
python3 src/smm_panel/main.py
```
Or via Uvicorn:
```bash
uvicorn smm_panel.app:create_app --factory --host 0.0.0.0 --port 8000 --reload
```

- **OpenAPI Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 🐳 Docker Deployment

```bash
docker compose up -d --build
docker compose logs -f
```

---

## 🧪 Automated Testing

```bash
PYTHONPATH=src pytest -v tests/
```

Test Results (24/24 passed — 100% pass rate):
```
tests/test_api_analytics_and_health.py::test_health_and_root PASSED      [  4%]
tests/test_api_analytics_and_health.py::test_analytics_dashboard PASSED  [  8%]
tests/test_api_analytics_and_health.py::test_provider_endpoints PASSED   [ 12%]
tests/test_api_analytics_and_health.py::test_promo_code_validation_endpoint PASSED [ 16%]
tests/test_api_orders.py::test_order_placement_flow PASSED               [ 20%]
tests/test_api_orders.py::test_order_insufficient_balance PASSED         [ 25%]
tests/test_api_orders.py::test_order_partial_refund PASSED               [ 29%]
tests/test_api_reseller_v2.py::test_v2_balance_action PASSED             [ 33%]
tests/test_api_reseller_v2.py::test_v2_services_action PASSED            [ 37%]
tests/test_api_reseller_v2.py::test_v2_add_and_status_action PASSED      [ 41%]
tests/test_api_reseller_v2.py::test_v2_auth_errors PASSED                [ 45%]
tests/test_api_services.py::test_list_and_filter_services PASSED         [ 50%]
tests/test_api_services.py::test_create_and_get_service PASSED           [ 54%]
tests/test_api_users.py::test_create_and_list_users PASSED               [ 58%]
tests/test_api_users.py::test_deposit_balance_and_transactions PASSED    [ 62%]
tests/test_api_users.py::test_user_not_found PASSED                      [ 66%]
tests/test_config.py::test_settings_defaults PASSED                      [ 70%]
tests/test_config.py::test_sqlite_path_resolution PASSED                 [ 75%]
tests/test_config.py::test_cached_settings PASSED                        [ 79%]
tests/test_database.py::test_initial_seeding PASSED                      [ 83%]
tests/test_database.py::test_user_balance_adjustment PASSED              [ 87%]
tests/test_database.py::test_insufficient_balance_error PASSED           [ 91%]
tests/test_database.py::test_order_placement_and_cancellation_refund PASSED [ 95%]
tests/test_database.py::test_promo_code_validation_and_exhaustion PASSED [100%]

============================== 24 passed in 7.56s ==============================
```

---

## 📡 API Endpoints Summary

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Service and database health check |
| `POST` | `/api/v2` | **Standard SMM v2 Reseller Endpoint** (`services`, `add`, `status`, `balance`) |
| `POST` | `/api/users` | Create user or reseller account |
| `GET` | `/api/users` | List registered accounts |
| `POST` | `/api/users/{id}/deposit` | Credit account balance |
| `GET` | `/api/users/{id}/transactions` | View financial transaction ledger |
| `POST` | `/api/services` | Add new catalog service |
| `GET` | `/api/services` | List catalog services (with platform filters) |
| `POST` | `/api/orders` | Place SMM order (with automated balance deduction) |
| `GET` | `/api/orders` | Query orders list |
| `PATCH` | `/api/orders/{id}` | Update status (triggers automatic cancellation/partial refunds) |
| `GET` | `/api/providers/{id}/balance` | Query live upstream provider balance |
| `POST` | `/api/promos/validate` | Validate promo code and preview discount |
| `GET` | `/api/analytics/dashboard` | Executive KPI and gross profit dashboard |

---

## 📄 License

MIT License.
Author: [Afzalbek](https://github.com/afzalbek-dev).
