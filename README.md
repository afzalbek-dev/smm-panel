# 🚀 SMM Panel — Ijtimoiy Tarmoqlar Marketingi va Reseller Agregator Tizimi

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.10+-e92063.svg)](https://docs.pydantic.dev/)
[![SQLite / aiosqlite](https://img.shields.io/badge/Database-aiosqlite-003B57.svg?logo=sqlite&logoColor=white)](https://sqlite.org)
[![Tests Passing](https://img.shields.io/badge/tests-24%2F24%20passed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**SMM Panel** — yuqori yuklamali, asinxron SMM provayderlari agregatori, buyurtmalar ijrosi, avtomatlashtirilgan balans va moliya jurnali hamda **Standard SMM API v2 Reseller protokoli** bilan to'liq jihozlangan zamonaviy platforma.

> 🌐 Hujjatlar boshqa tillarda: [English (README.en.md)](README.en.md) | [Русский (README.ru.md)](README.ru.md)

---

## 🌟 Asosiy Imkoniyatlar

- **🔌 Standart SMM API v2 Reseller Protokoli:**
  - Perfect Panel, JAP va boshqa barcha reseller panellar bilan 100% moslik.
  - `action=services`: Faol xizmatlar, narxlar va limitlar ro'yxati.
  - `action=add`: Buyurtma berish, balansdan avtomatik yechish va provayderga jo'natish.
  - `action=status`: Bitta yoki vergul bilan ajratilgan ko'p buyurtmalar holatini tekshirish.
  - `action=balance`: Reseller balansini real vaqtda so'rash.

- **💳 Atomik Moliyaviy Balans va Tranzaksiyalar (Ledger):**
  - Foydalanuvchi hisobidan pul yechish va to'ldirish poyga holatlarisiz (race condition) xavfsiz amalga oshiriladi.
  - Manfiy balansga tushishdan kafolatlangan himoya.
  - Har bir depozit, buyurtma to'lovi va qaytarish (refund) uchun o'zgarmas moliyaviy audit jurnali.

- **🔄 Avtomatik Qaytarish (Refunds) Mantiqi:**
  - Bekor qilingan (`cancelled`) buyurtmalar to'lovi to'liq avtomatik tarzda balansga qaytadi.
  - Qisman bajarilgan (`partial`) buyurtmalarda bajarilmagan qoldiq (`remains`) hisoblanib, proporsional mablag' qaytariladi.

- **🌐 Ko'p Provayderli Arxitektura va Mock Driver:**
  - Bir nechta tashqi provayderlarni qo'shish va ular balansi hamda xizmatlarini sinxronizatsiya qilish.
  - Maxfiy API kalitlari bo'lmagan holda yoki oflayn testlar uchun to'liq ishlaydigan **Mock Provider Driver**.

- **🎁 Promo Kodlar va Chegirmalar Tizimi:**
  - Foizli yoki bonusli promo kodlarni kiritish, amal qilish muddati va foydalanish limitlarini boshqarish.
  - Resellerlar uchun shaxsiy foizli chegirmalar (`discount_percent`).

- **📈 Ijrochi Analitika Paneli (Dashboard):**
  - Jami buyurtmalar, umumiy tushum ($), provayder tannarxi, sof foyda (Gross Profit) va rentabellik marjasi (Profit Margin %).
  - Ijtimoiy tarmoqlar (Telegram, Instagram, YouTube, TikTok, X) bo'yicha hajm va daromad kesimi.

---

## 🏗 Kataloglar va Arxitektura Tuzilishi

```
smm-panel/
├── src/smm_panel/
│   ├── api/
│   │   ├── dependencies.py         # FastAPI dependency injection
│   │   ├── routes_users.py         # Foydalanuvchilar, depozitlar va tranzaksiyalar
│   │   ├── routes_services.py      # Xizmatlar katalogi (Telegram, Instagram, va h.k.)
│   │   ├── routes_orders.py        # Buyurtmalar boshqaruvi va avtomatik refund
│   │   ├── routes_providers.py     # SMM API provayderlari boshqaruvi va balans sync
│   │   ├── routes_reseller_v2.py   # Standart SMM v2 Reseller protokoli endpointi
│   │   ├── routes_promos.py        # Promo kodlar tizimi
│   │   └── routes_analytics.py     # Boshqaruv paneli KPI analitikasi
│   ├── database/
│   │   └── repository.py           # Asinxron aiosqlite repository qatlami
│   ├── models/
│   │   ├── user.py                 # Foydalanuvchilar va tranzaksiyalar modellari
│   │   ├── service.py              # Xizmatlar va platformalar modellari
│   │   ├── order.py                # Buyurtmalar va SMM v2 protokoli shartnomalari
│   │   ├── provider.py             # Provayderlar modellari
│   │   ├── promo.py                # Promo kodlar modellari
│   │   └── analytics.py            # Boshqaruv paneli modellari
│   ├── providers/
│   │   ├── base.py                 # Provayder drayver interfeysi
│   │   ├── standard_smm.py         # Jonli HTTP provayder mijozi (httpx)
│   │   └── mock_provider.py        # Oflayn deterministik sinov drayveri
│   ├── app.py                      # FastAPI factory va CORS
│   ├── config.py                   # Pydantic konfiguratsiyasi
│   └── main.py                     # Uvicorn server launcher
├── tests/
│   ├── conftest.py                 # Pytest fixturalari va xotiradagi test bazasi
│   ├── test_config.py              # Konfiguratsiya testlari
│   ├── test_database.py            # Baza, atomik balans va refund testlari
│   ├── test_api_users.py           # Foydalanuvchilar API testlari
│   ├── test_api_services.py        # Xizmatlar katalogi API testlari
│   ├── test_api_orders.py          # Buyurtmalar va qisman refund testlari
│   ├── test_api_reseller_v2.py     # SMM v2 Reseller protokoli testlari
│   └── test_api_analytics_and_health.py # Analitika va tizim salomatligi testlari
├── Dockerfile                      # Production Docker container
├── docker-compose.yml              # Konteyner manifesti
├── pyproject.toml                  # Python metama'lumotlari
├── requirements.txt                # Kutubxonalar ro'yxati
└── .env.example                    # Muhit o'zgaruvchilari namunasi
```

---

## 🚀 O'rnatish va Ishga Tushirish

### 1. Talablar
- Python 3.11+
- Git

### 2. Virtual muhit va bog'liqliklar
```bash
git clone https://github.com/afzalbek-dev/smm-panel.git
cd smm-panel

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Konfiguratsiyani sozlash
```bash
cp .env.example .env
```
`.env` faylidagi asosiy sozlamalar:
```env
APP_ENV=production
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./smm_panel.db
USE_MOCK_PROVIDER=true
LOG_LEVEL=INFO
```

### 4. Serverni ishga tushirish
```bash
python3 src/smm_panel/main.py
```
Yoki to'g'ridan-to'g'ri Uvicorn orqali:
```bash
uvicorn smm_panel.app:create_app --factory --host 0.0.0.0 --port 8000 --reload
```

- **Swagger Hujjatlari:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Hujjatlari:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Salomatlik tekshiruvi:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 🐳 Docker orqali ishga tushirish

```bash
docker compose up -d --build
docker compose logs -f
```

---

## 🧪 Avtomatlashtirilgan Testlar

```bash
PYTHONPATH=src pytest -v tests/
```

Test natijasi (24/24 passed — 100% muvaffaqiyatli):
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

## 📡 API Manzillari Jadvali

| Metod | Yo'l | Tavsif |
|---|---|---|
| `GET` | `/health` | Xizmat va baza salomatlik holati |
| `POST` | `/api/v2` | **Standart SMM v2 protokoli** (`services`, `add`, `status`, `balance`) |
| `POST` | `/api/users` | Yangi foydalanuvchi yoki reseller yaratish |
| `GET` | `/api/users` | Foydalanuvchilar ro'yxati |
| `POST` | `/api/users/{id}/deposit` | Foydalanuvchi balansini to'ldirish |
| `GET` | `/api/users/{id}/transactions` | Tranzaksiyalar va moliya jurnali |
| `POST` | `/api/services` | Yangi xizmat qo'shish |
| `GET` | `/api/services` | Xizmatlar katalogi (platforma bo'yicha filtr) |
| `POST` | `/api/orders` | Yangi buyurtma berish (balans nazorati bilan) |
| `GET` | `/api/orders` | Buyurtmalar ro'yxati |
| `PATCH` | `/api/orders/{id}` | Status yangilash (avtomatik bekor qilish va qisman refund) |
| `GET` | `/api/providers/{id}/balance` | Tashqi provayder balansini sinxronlash |
| `POST` | `/api/promos/validate` | Promo kodni tekshirish va chegirma hisoblash |
| `GET` | `/api/analytics/dashboard` | Boshqaruv paneli tahlili va rentabellik ko'rsatkichlari |

---

## 📄 Litsenziya

MIT Litsenziyasi ostida tarqatiladi.
Muallif: [Afzalbek](https://github.com/afzalbek-dev).
