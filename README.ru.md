# 🚀 SMM Panel — Агрегатор SMM-Провайдеров и Платформа Выполнения Заказов

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.10+-e92063.svg)](https://docs.pydantic.dev/)
[![SQLite / aiosqlite](https://img.shields.io/badge/Database-aiosqlite-003B57.svg?logo=sqlite&logoColor=white)](https://sqlite.org)
[![Tests Passing](https://img.shields.io/badge/tests-24%2F24%20passed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**SMM Panel** — высокопроизводительная асинхронная платформа для автоматизации услуг продвижения в социальных сетях, агрегации SMM-провайдеров, учета клиентских балансов и выполнения заказов с поддержкой **стандартного протокола SMM API v2**.

> 🌐 Документация на других языках: [O'zbekcha (README.md)](README.md) | [English (README.en.md)](README.en.md)

---

## 🌟 Основные Возможности

- **🔌 Стандартный Протокол SMM API v2:**
  - Полная совместимость со всеми реселлер-панелями (Perfect Panel, JAP и др.).
  - `action=services`: Каталог активных услуг, цен и лимитов.
  - `action=add`: Оформление заказа, списание средств и передача провайдеру.
  - `action=status`: Проверка статуса одиночного заказа или списка заказов через запятую.
  - `action=balance`: Мгновенный запрос текущего баланса реселлера.

- **💳 Атомарный Финансовый Леджер и Балансы:**
  - Полная защита от race condition и ухода в отрицательный баланс.
  - Неизменяемый журнал всех пополнений, списаний и возвратов (Transactions).

- **🔄 Автоматические Возвраты Средств (Refunds):**
  - При отмене заказа (`cancelled`) сумма блокировки мгновенно возвращается на баланс.
  - При частичном выполнении (`partial`) вычисляется невыполненный остаток (`remains`) и начисляется пропорциональный возврат.

- **🌐 Мульти-Провайдерная Архитектура и Mock Driver:**
  - Управление несколькими внешними провайдерами и синхронизация балансов.
  - Встроенный детерминированный **Mock Provider Driver** для запуска без боевых ключей и офлайн-тестирования.

- **🎁 Промокоды и Скидочные Уровни:**
  - Промокоды на скидку в процентах или фиксированный денежный бонус.
  - Персональные скидки для реселлеров (`discount_percent`).

- **📈 Аналитический Дашборд Руководителя:**
  - Сводка по заказам, общий оборот ($), затраты на провайдеров, валовая прибыль (Gross Profit), маржинальность (Profit Margin %) и статистика по платформам (Telegram, Instagram, YouTube, TikTok, X).

---

## 🏗 Архитектура и Структура Файлов

```
smm-panel/
├── src/smm_panel/
│   ├── api/
│   │   ├── dependencies.py         # Внедрение зависимостей FastAPI
│   │   ├── routes_users.py         # Пользователи, балансы и транзакции
│   │   ├── routes_services.py      # Каталог услуг с фильтрами по платформам
│   │   ├── routes_orders.py        # Управление заказами и возвратами
│   │   ├── routes_providers.py     # Провайдеры и синхронизация баланса
│   │   ├── routes_reseller_v2.py   # Обработчик стандартного протокола SMM v2
│   │   ├── routes_promos.py        # Маркетинговые промокоды
│   │   └── routes_analytics.py     # Дашборд ключевых показателей бизнеса
│   ├── database/
│   │   └── repository.py           # Асинхронный SQLite репозиторий (aiosqlite)
│   ├── models/
│   │   ├── user.py                 # Модели пользователей и транзакций
│   │   ├── service.py              # Модели каталога услуг
│   │   ├── order.py                # Модели заказов и контракты протокола v2
│   │   ├── provider.py             # Модели внешних провайдеров
│   │   ├── promo.py                # Модели промокодов
│   │   └── analytics.py            # Модели бизнес-метрик
│   ├── providers/
│   │   ├── base.py                 # Абстрактный интерфейс провайдера
│   │   ├── standard_smm.py         # Боевой HTTP клиент (httpx)
│   │   └── mock_provider.py        # Офлайн mock-драйвер для тестов
│   ├── app.py                      # Фабрика приложения FastAPI
│   ├── config.py                   # Конфигурация Pydantic
│   └── main.py                     # Скрипт запуска Uvicorn
├── tests/
│   ├── conftest.py                 # Фикстуры pytest
│   ├── test_config.py              # Тесты конфигурации
│   ├── test_database.py            # Тесты БД, леджера и логики возвратов
│   ├── test_api_users.py           # Тесты API пользователей
│   ├── test_api_services.py        # Тесты каталога услуг
│   ├── test_api_orders.py          # Тесты заказов и частичных возвратов
│   ├── test_api_reseller_v2.py     # Тесты реселлерского протокола v2
│   └── test_api_analytics_and_health.py # Тесты аналитики и health-чека
├── Dockerfile                      # Production Docker-образ
├── docker-compose.yml              # Манифест Docker Compose
├── pyproject.toml                  # Конфигурация пакета Python
├── requirements.txt                # Зависимости
└── .env.example                    # Пример переменных окружения
```

---

## 🚀 Установка и Запуск

### Требования
- Python 3.11+
- Git

### 1. Клонирование и настройка окружения
```bash
git clone https://github.com/afzalbek-dev/smm-panel.git
cd smm-panel

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Настройка переменных окружения
```bash
cp .env.example .env
```
Основные параметры:
```env
APP_ENV=production
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./smm_panel.db
USE_MOCK_PROVIDER=true
LOG_LEVEL=INFO
```

### 3. Запуск сервера
```bash
python3 src/smm_panel/main.py
```
Или напрямую через Uvicorn:
```bash
uvicorn smm_panel.app:create_app --factory --host 0.0.0.0 --port 8000 --reload
```

- **OpenAPI Документация:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Документация:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Проверка здоровья (Health Check):** [http://localhost:8000/health](http://localhost:8000/health)

---

## 🐳 Запуск через Docker

```bash
docker compose up -d --build
docker compose logs -f
```

---

## 🧪 Запуск Тестов

```bash
PYTHONPATH=src pytest -v tests/
```

Результаты тестов (24/24 passed — 100%):
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

## 📄 Лицензия

Распространяется под лицензией MIT.
Автор: [Afzalbek](https://github.com/afzalbek-dev).
