"""Async SQLite database repository for SMM Panel."""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import aiosqlite

from smm_panel.models.user import (
    User,
    UserCreate,
    UserUpdate,
    UserRole,
    Transaction,
    TransactionType,
)
from smm_panel.models.service import (
    Service,
    ServiceCreate,
    ServiceUpdate,
    Platform,
    ServiceType,
)
from smm_panel.models.provider import (
    Provider,
    ProviderCreate,
    ProviderUpdate,
)
from smm_panel.models.order import (
    Order,
    OrderCreate,
    OrderUpdate,
    OrderStatus,
)
from smm_panel.models.promo import (
    PromoCode,
    PromoCodeCreate,
    PromoApplyResult,
)
from smm_panel.models.analytics import (
    PlatformMetric,
    SmmDashboardMetrics,
)

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SmmRepository:
    """Asynchronous SQLite Repository managing all SMM Panel operations."""

    def __init__(self, db_path: Path):
        self.db_path = db_path

    async def init_db(self) -> None:
        """Create tables, indexes, and seed default catalog if empty."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON;")

            # 1. Users table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    role TEXT DEFAULT 'user',
                    balance_usd REAL DEFAULT 0.0,
                    discount_percent REAL DEFAULT 0.0,
                    api_key TEXT UNIQUE NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 2. Transactions table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    amount_usd REAL NOT NULL,
                    balance_after REAL NOT NULL,
                    description TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
            """)

            # 3. Providers table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS providers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    api_url TEXT NOT NULL,
                    api_key TEXT NOT NULL,
                    balance_usd REAL DEFAULT 0.0,
                    currency TEXT DEFAULT 'USD',
                    is_active INTEGER DEFAULT 1,
                    last_sync_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 4. Services table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    service_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    rate_per_1k REAL NOT NULL,
                    min_quantity INTEGER DEFAULT 10,
                    max_quantity INTEGER DEFAULT 100000,
                    provider_id INTEGER,
                    provider_service_id INTEGER,
                    provider_rate_per_1k REAL DEFAULT 0.0,
                    is_active INTEGER DEFAULT 1,
                    refill_supported INTEGER DEFAULT 1,
                    description TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (provider_id) REFERENCES providers(id) ON DELETE SET NULL
                );
            """)

            # 5. Orders table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    service_id INTEGER NOT NULL,
                    link TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    charge_usd REAL NOT NULL,
                    provider_cost_usd REAL DEFAULT 0.0,
                    start_count INTEGER DEFAULT 0,
                    remains INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    provider_id INTEGER,
                    provider_order_id TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE RESTRICT
                );
            """)

            # 6. Promo Codes table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS promo_codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    discount_percent REAL DEFAULT 0.0,
                    bonus_usd REAL DEFAULT 0.0,
                    max_uses INTEGER DEFAULT 100,
                    times_used INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            await db.commit()

        # Seed initial defaults
        await self._seed_defaults()
        logger.info("SMM Panel database initialized and verified.")

    async def _seed_defaults(self) -> None:
        """Seed default admin, mock provider, and starter services if empty."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM users")
            user_count = (await cursor.fetchone())[0]

            if user_count == 0:
                now_iso = utc_now().isoformat()
                # Create admin
                await db.execute(
                    """
                    INSERT INTO users (username, email, role, balance_usd, discount_percent, api_key, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
                    """,
                    ("admin", "admin@smm.local", UserRole.ADMIN.value, 500.0, 0.0, "smm_admin_secret_key_2026", now_iso, now_iso),
                )
                # Create demo reseller
                await db.execute(
                    """
                    INSERT INTO users (username, email, role, balance_usd, discount_percent, api_key, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
                    """,
                    ("reseller_pro", "partner@reseller.io", UserRole.RESELLER.value, 150.0, 15.0, "smm_reseller_api_key_demo", now_iso, now_iso),
                )

                # Create mock provider
                cursor = await db.execute(
                    """
                    INSERT INTO providers (name, api_url, api_key, balance_usd, currency, is_active, last_sync_at, created_at)
                    VALUES (?, ?, ?, ?, ?, 1, ?, ?)
                    """,
                    ("Global SMM Main Hub", "https://mock-provider.smm.internal/api/v2", "mock_prov_sec_99", 2500.0, "USD", now_iso, now_iso),
                )
                prov_id = cursor.lastrowid

                # Seed core services
                services = [
                    ("Telegram Channel Members [High Speed]", Platform.TELEGRAM.value, ServiceType.FOLLOWERS.value, "Telegram", 1.20, 50, 50000, prov_id, 101, 0.60, 1, "Real and active Telegram subscribers with 30-day refill"),
                    ("Telegram Post Views [Instant]", Platform.TELEGRAM.value, ServiceType.VIEWS.value, "Telegram", 0.10, 100, 100000, prov_id, 102, 0.03, 0, "Instant delivery views for any public Telegram post"),
                    ("Instagram Followers [Organic Mix]", Platform.INSTAGRAM.value, ServiceType.FOLLOWERS.value, "Instagram", 1.80, 50, 30000, prov_id, 103, 0.90, 1, "High quality profile followers with non-drop guarantee"),
                    ("Instagram Likes [Instant]", Platform.INSTAGRAM.value, ServiceType.LIKES.value, "Instagram", 0.45, 20, 20000, prov_id, 104, 0.15, 0, "Instant engagement likes"),
                    ("YouTube Video Views [Retention Safe]", Platform.YOUTUBE.value, ServiceType.VIEWS.value, "YouTube", 2.50, 500, 50000, prov_id, 105, 1.20, 1, "Monetization safe video views"),
                    ("TikTok Video Views [Viral Speed]", Platform.TIKTOK.value, ServiceType.VIEWS.value, "TikTok", 0.15, 100, 200000, prov_id, 106, 0.04, 0, "High velocity viral impressions"),
                ]

                for s in services:
                    await db.execute(
                        """
                        INSERT INTO services (
                            name, platform, service_type, category, rate_per_1k, min_quantity,
                            max_quantity, provider_id, provider_service_id, provider_rate_per_1k,
                            is_active, refill_supported, description, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?)
                        """,
                        (s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8], s[9], s[10], s[11], now_iso, now_iso),
                    )

                # Seed sample promo code
                await db.execute(
                    """
                    INSERT INTO promo_codes (code, discount_percent, bonus_usd, max_uses, times_used, is_active, created_at)
                    VALUES ('START2026', 10.0, 5.0, 500, 0, 1, ?)
                    """,
                    (now_iso,),
                )

                await db.commit()

    # --- User Operations ---
    async def create_user(self, payload: UserCreate) -> User:
        now_iso = utc_now().isoformat()
        import secrets
        api_key = f"smm_{secrets.token_hex(16)}"

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO users (username, email, role, balance_usd, discount_percent, api_key, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
                """,
                (payload.username, payload.email, payload.role.value, payload.balance_usd, payload.discount_percent, api_key, now_iso, now_iso),
            )
            uid = cursor.lastrowid

            if payload.balance_usd > 0:
                await db.execute(
                    """
                    INSERT INTO transactions (user_id, type, amount_usd, balance_after, description, created_at)
                    VALUES (?, ?, ?, ?, 'Initial balance', ?)
                    """,
                    (uid, TransactionType.DEPOSIT.value, payload.balance_usd, payload.balance_usd, now_iso),
                )

            await db.commit()
            return User(
                id=uid,
                username=payload.username,
                email=payload.email,
                role=payload.role,
                balance_usd=payload.balance_usd,
                discount_percent=payload.discount_percent,
                api_key=api_key,
                is_active=True,
                created_at=utc_now(),
                updated_at=utc_now(),
            )

    async def get_users(self) -> List[User]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, username, email, role, balance_usd, discount_percent, api_key, is_active, created_at, updated_at FROM users ORDER BY id ASC"
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    User(
                        id=r[0],
                        username=r[1],
                        email=r[2],
                        role=UserRole(r[3]),
                        balance_usd=r[4],
                        discount_percent=r[5],
                        api_key=r[6],
                        is_active=bool(r[7]),
                        created_at=datetime.fromisoformat(r[8]) if isinstance(r[8], str) else r[8],
                        updated_at=datetime.fromisoformat(r[9]) if isinstance(r[9], str) else r[9],
                    )
                    for r in rows
                ]

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, username, email, role, balance_usd, discount_percent, api_key, is_active, created_at, updated_at FROM users WHERE id = ?",
                (user_id,),
            ) as cursor:
                r = await cursor.fetchone()
                if not r:
                    return None
                return User(
                    id=r[0],
                    username=r[1],
                    email=r[2],
                    role=UserRole(r[3]),
                    balance_usd=r[4],
                    discount_percent=r[5],
                    api_key=r[6],
                    is_active=bool(r[7]),
                    created_at=datetime.fromisoformat(r[8]) if isinstance(r[8], str) else r[8],
                    updated_at=datetime.fromisoformat(r[9]) if isinstance(r[9], str) else r[9],
                )

    async def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, username, email, role, balance_usd, discount_percent, api_key, is_active, created_at, updated_at FROM users WHERE api_key = ?",
                (api_key,),
            ) as cursor:
                r = await cursor.fetchone()
                if not r:
                    return None
                return User(
                    id=r[0],
                    username=r[1],
                    email=r[2],
                    role=UserRole(r[3]),
                    balance_usd=r[4],
                    discount_percent=r[5],
                    api_key=r[6],
                    is_active=bool(r[7]),
                    created_at=datetime.fromisoformat(r[8]) if isinstance(r[8], str) else r[8],
                    updated_at=datetime.fromisoformat(r[9]) if isinstance(r[9], str) else r[9],
                )

    async def adjust_user_balance(
        self, user_id: int, amount: float, tx_type: TransactionType, description: str = ""
    ) -> User:
        """Atomically adjust user balance and record ledger transaction."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT balance_usd FROM users WHERE id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise ValueError(f"User with id {user_id} not found")
                current_bal = row[0]

            new_bal = round(current_bal + amount, 4)
            if new_bal < 0:
                raise ValueError("Insufficient balance")

            now_iso = utc_now().isoformat()
            await db.execute(
                "UPDATE users SET balance_usd = ?, updated_at = ? WHERE id = ?",
                (new_bal, now_iso, user_id),
            )

            await db.execute(
                """
                INSERT INTO transactions (user_id, type, amount_usd, balance_after, description, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, tx_type.value, amount, new_bal, description, now_iso),
            )
            await db.commit()

        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} missing after update")
        return user

    async def get_transactions(self, user_id: Optional[int] = None) -> List[Transaction]:
        query = "SELECT id, user_id, type, amount_usd, balance_after, description, created_at FROM transactions WHERE 1=1"
        params = []
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        query += " ORDER BY id DESC"

        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [
                    Transaction(
                        id=r[0],
                        user_id=r[1],
                        type=TransactionType(r[2]),
                        amount_usd=r[3],
                        balance_after=r[4],
                        description=r[5] or "",
                        created_at=datetime.fromisoformat(r[6]) if isinstance(r[6], str) else r[6],
                    )
                    for r in rows
                ]

    # --- Services Operations ---
    async def create_service(self, payload: ServiceCreate) -> Service:
        now_iso = utc_now().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO services (
                    name, platform, service_type, category, rate_per_1k, min_quantity,
                    max_quantity, provider_id, provider_service_id, provider_rate_per_1k,
                    is_active, refill_supported, description, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?)
                """,
                (
                    payload.name,
                    payload.platform.value,
                    payload.service_type.value,
                    payload.category,
                    payload.rate_per_1k,
                    payload.min_quantity,
                    payload.max_quantity,
                    payload.provider_id,
                    payload.provider_service_id,
                    payload.provider_rate_per_1k or 0.0,
                    1 if payload.refill_supported else 0,
                    payload.description or "",
                    now_iso,
                    now_iso,
                ),
            )
            await db.commit()
            return Service(
                id=cursor.lastrowid,
                name=payload.name,
                platform=payload.platform,
                service_type=payload.service_type,
                category=payload.category,
                rate_per_1k=payload.rate_per_1k,
                min_quantity=payload.min_quantity,
                max_quantity=payload.max_quantity,
                provider_id=payload.provider_id,
                provider_service_id=payload.provider_service_id,
                provider_rate_per_1k=payload.provider_rate_per_1k or 0.0,
                is_active=True,
                refill_supported=payload.refill_supported,
                description=payload.description or "",
                created_at=utc_now(),
                updated_at=utc_now(),
            )

    async def get_services(
        self, platform: Optional[Platform] = None, is_active: Optional[bool] = None
    ) -> List[Service]:
        query = "SELECT id, name, platform, service_type, category, rate_per_1k, min_quantity, max_quantity, provider_id, provider_service_id, provider_rate_per_1k, is_active, refill_supported, description, created_at, updated_at FROM services WHERE 1=1"
        params = []
        if platform:
            query += " AND platform = ?"
            params.append(platform.value)
        if is_active is not None:
            query += " AND is_active = ?"
            params.append(1 if is_active else 0)
        query += " ORDER BY id ASC"

        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [
                    Service(
                        id=r[0],
                        name=r[1],
                        platform=Platform(r[2]),
                        service_type=ServiceType(r[3]),
                        category=r[4],
                        rate_per_1k=r[5],
                        min_quantity=r[6],
                        max_quantity=r[7],
                        provider_id=r[8],
                        provider_service_id=r[9],
                        provider_rate_per_1k=r[10] or 0.0,
                        is_active=bool(r[11]),
                        refill_supported=bool(r[12]),
                        description=r[13] or "",
                        created_at=datetime.fromisoformat(r[14]) if isinstance(r[14], str) else r[14],
                        updated_at=datetime.fromisoformat(r[15]) if isinstance(r[15], str) else r[15],
                    )
                    for r in rows
                ]

    async def get_service_by_id(self, service_id: int) -> Optional[Service]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, name, platform, service_type, category, rate_per_1k, min_quantity, max_quantity, provider_id, provider_service_id, provider_rate_per_1k, is_active, refill_supported, description, created_at, updated_at FROM services WHERE id = ?",
                (service_id,),
            ) as cursor:
                r = await cursor.fetchone()
                if not r:
                    return None
                return Service(
                    id=r[0],
                    name=r[1],
                    platform=Platform(r[2]),
                    service_type=ServiceType(r[3]),
                    category=r[4],
                    rate_per_1k=r[5],
                    min_quantity=r[6],
                    max_quantity=r[7],
                    provider_id=r[8],
                    provider_service_id=r[9],
                    provider_rate_per_1k=r[10] or 0.0,
                    is_active=bool(r[11]),
                    refill_supported=bool(r[12]),
                    description=r[13] or "",
                    created_at=datetime.fromisoformat(r[14]) if isinstance(r[14], str) else r[14],
                    updated_at=datetime.fromisoformat(r[15]) if isinstance(r[15], str) else r[15],
                )

    # --- Provider Operations ---
    async def create_provider(self, payload: ProviderCreate) -> Provider:
        now_iso = utc_now().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO providers (name, api_url, api_key, balance_usd, currency, is_active, last_sync_at, created_at)
                VALUES (?, ?, ?, 0.0, 'USD', ?, ?, ?)
                """,
                (payload.name, payload.api_url, payload.api_key, 1 if payload.is_active else 0, now_iso, now_iso),
            )
            await db.commit()
            return Provider(
                id=cursor.lastrowid,
                name=payload.name,
                api_url=payload.api_url,
                api_key=payload.api_key,
                balance_usd=0.0,
                currency="USD",
                is_active=payload.is_active,
                last_sync_at=utc_now(),
                created_at=utc_now(),
            )

    async def get_providers(self) -> List[Provider]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, name, api_url, api_key, balance_usd, currency, is_active, last_sync_at, created_at FROM providers ORDER BY id ASC"
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    Provider(
                        id=r[0],
                        name=r[1],
                        api_url=r[2],
                        api_key=r[3],
                        balance_usd=r[4] or 0.0,
                        currency=r[5] or "USD",
                        is_active=bool(r[6]),
                        last_sync_at=datetime.fromisoformat(r[7]) if r[7] else None,
                        created_at=datetime.fromisoformat(r[8]) if isinstance(r[8], str) else r[8],
                    )
                    for r in rows
                ]

    async def get_provider_by_id(self, provider_id: int) -> Optional[Provider]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, name, api_url, api_key, balance_usd, currency, is_active, last_sync_at, created_at FROM providers WHERE id = ?",
                (provider_id,),
            ) as cursor:
                r = await cursor.fetchone()
                if not r:
                    return None
                return Provider(
                    id=r[0],
                    name=r[1],
                    api_url=r[2],
                    api_key=r[3],
                    balance_usd=r[4] or 0.0,
                    currency=r[5] or "USD",
                    is_active=bool(r[6]),
                    last_sync_at=datetime.fromisoformat(r[7]) if r[7] else None,
                    created_at=datetime.fromisoformat(r[8]) if isinstance(r[8], str) else r[8],
                )

    async def update_provider_balance(self, provider_id: int, balance: float) -> None:
        now_iso = utc_now().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE providers SET balance_usd = ?, last_sync_at = ? WHERE id = ?",
                (balance, now_iso, provider_id),
            )
            await db.commit()

    # --- Promo Code Operations ---
    async def create_promo_code(self, payload: PromoCodeCreate) -> PromoCode:
        now_iso = utc_now().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO promo_codes (code, discount_percent, bonus_usd, max_uses, times_used, is_active, created_at)
                VALUES (?, ?, ?, ?, 0, 1, ?)
                """,
                (payload.code.upper(), payload.discount_percent, payload.bonus_usd, payload.max_uses, now_iso),
            )
            await db.commit()
            return PromoCode(
                id=cursor.lastrowid,
                code=payload.code.upper(),
                discount_percent=payload.discount_percent,
                bonus_usd=payload.bonus_usd,
                max_uses=payload.max_uses,
                times_used=0,
                is_active=True,
                created_at=utc_now(),
            )

    async def validate_and_apply_promo(self, code_str: str) -> PromoApplyResult:
        code_clean = code_str.strip().upper()
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, code, discount_percent, bonus_usd, max_uses, times_used, is_active FROM promo_codes WHERE code = ?",
                (code_clean,),
            ) as cursor:
                r = await cursor.fetchone()
                if not r:
                    return PromoApplyResult(valid=False, message="Promo code does not exist")
                if not r[6]:
                    return PromoApplyResult(valid=False, message="Promo code is inactive")
                if r[5] >= r[4]:
                    return PromoApplyResult(valid=False, message="Promo code has reached max redemption limit")

                # Increment usage
                await db.execute(
                    "UPDATE promo_codes SET times_used = times_used + 1 WHERE id = ?", (r[0],)
                )
                await db.commit()

                return PromoApplyResult(
                    valid=True,
                    discount_percent=r[2],
                    bonus_usd=r[3],
                    message=f"Promo code {code_clean} applied successfully",
                )

    # --- Order Operations ---
    async def place_order(
        self,
        payload: OrderCreate,
        provider_driver: Optional[Any] = None,
    ) -> Order:
        """Place SMM order: validate constraints, calculate charge, deduct balance, forward to provider."""
        # 1. Fetch user
        user = await self.get_user_by_id(payload.user_id)
        if not user or not user.is_active:
            raise ValueError("Active user not found")

        # 2. Fetch service
        service = await self.get_service_by_id(payload.service_id)
        if not service or not service.is_active:
            raise ValueError("Active service not found")

        # 3. Validate quantity bounds
        if payload.quantity < service.min_quantity or payload.quantity > service.max_quantity:
            raise ValueError(
                f"Quantity must be between {service.min_quantity} and {service.max_quantity}"
            )

        # 4. Calculate charge
        base_charge = (payload.quantity / 1000.0) * service.rate_per_1k

        # Apply user discount
        user_discount = (user.discount_percent / 100.0) * base_charge
        charge_after_user_disc = base_charge - user_discount

        # Apply promo code if provided
        promo_discount = 0.0
        if payload.promo_code:
            promo_res = await self.validate_and_apply_promo(payload.promo_code)
            if promo_res.valid:
                promo_discount = (promo_res.discount_percent / 100.0) * charge_after_user_disc

        final_charge = round(max(0.01, charge_after_user_disc - promo_discount), 4)

        # Calculate provider cost
        prov_cost = round((payload.quantity / 1000.0) * (service.provider_rate_per_1k or 0.0), 4)

        # 5. Atomically deduct balance
        await self.adjust_user_balance(
            user.id,
            -final_charge,
            TransactionType.ORDER_CHARGE,
            f"Order for service #{service.id} ({payload.quantity} qty)",
        )

        # 6. Forward to upstream provider if configured
        prov_order_id = ""
        initial_status = OrderStatus.IN_PROGRESS
        if service.provider_id and provider_driver:
            provider = await self.get_provider_by_id(service.provider_id)
            if provider and provider.is_active:
                try:
                    res = await provider_driver.place_order(
                        api_url=provider.api_url,
                        api_key=provider.api_key,
                        service_id=service.provider_service_id or service.id,
                        link=payload.link,
                        quantity=payload.quantity,
                        comments=payload.comments,
                    )
                    prov_order_id = str(res.get("order", ""))
                except Exception as e:
                    logger.warning(f"Upstream provider call error: {e}")
                    initial_status = OrderStatus.PENDING

        now_iso = utc_now().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO orders (
                    user_id, service_id, link, quantity, charge_usd, provider_cost_usd,
                    start_count, remains, status, provider_id, provider_order_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user.id,
                    service.id,
                    payload.link,
                    payload.quantity,
                    final_charge,
                    prov_cost,
                    payload.quantity,
                    initial_status.value,
                    service.provider_id,
                    prov_order_id,
                    now_iso,
                    now_iso,
                ),
            )
            order_id = cursor.lastrowid
            await db.commit()

        return Order(
            id=order_id,
            user_id=user.id,
            service_id=service.id,
            link=payload.link,
            quantity=payload.quantity,
            charge_usd=final_charge,
            provider_cost_usd=prov_cost,
            start_count=0,
            remains=payload.quantity,
            status=initial_status,
            provider_id=service.provider_id,
            provider_order_id=prov_order_id,
            created_at=utc_now(),
            updated_at=utc_now(),
        )

    async def get_orders(
        self,
        user_id: Optional[int] = None,
        status: Optional[OrderStatus] = None,
        service_id: Optional[int] = None,
    ) -> List[Order]:
        query = "SELECT id, user_id, service_id, link, quantity, charge_usd, provider_cost_usd, start_count, remains, status, provider_id, provider_order_id, created_at, updated_at FROM orders WHERE 1=1"
        params = []
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        if status:
            query += " AND status = ?"
            params.append(status.value)
        if service_id:
            query += " AND service_id = ?"
            params.append(service_id)
        query += " ORDER BY id DESC"

        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [
                    Order(
                        id=r[0],
                        user_id=r[1],
                        service_id=r[2],
                        link=r[3],
                        quantity=r[4],
                        charge_usd=r[5],
                        provider_cost_usd=r[6] or 0.0,
                        start_count=r[7] or 0,
                        remains=r[8] or 0,
                        status=OrderStatus(r[9]),
                        provider_id=r[10],
                        provider_order_id=r[11] or "",
                        created_at=datetime.fromisoformat(r[12]) if isinstance(r[12], str) else r[12],
                        updated_at=datetime.fromisoformat(r[13]) if isinstance(r[13], str) else r[13],
                    )
                    for r in rows
                ]

    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, user_id, service_id, link, quantity, charge_usd, provider_cost_usd, start_count, remains, status, provider_id, provider_order_id, created_at, updated_at FROM orders WHERE id = ?",
                (order_id,),
            ) as cursor:
                r = await cursor.fetchone()
                if not r:
                    return None
                return Order(
                    id=r[0],
                    user_id=r[1],
                    service_id=r[2],
                    link=r[3],
                    quantity=r[4],
                    charge_usd=r[5],
                    provider_cost_usd=r[6] or 0.0,
                    start_count=r[7] or 0,
                    remains=r[8] or 0,
                    status=OrderStatus(r[9]),
                    provider_id=r[10],
                    provider_order_id=r[11] or "",
                    created_at=datetime.fromisoformat(r[12]) if isinstance(r[12], str) else r[12],
                    updated_at=datetime.fromisoformat(r[13]) if isinstance(r[13], str) else r[13],
                )

    async def update_order_status(
        self, order_id: int, payload: OrderUpdate
    ) -> Optional[Order]:
        """Update order status and handle automatic refunds on cancellation or partial completion."""
        existing = await self.get_order_by_id(order_id)
        if not existing:
            return None

        new_status = payload.status if payload.status is not None else existing.status
        new_start = payload.start_count if payload.start_count is not None else existing.start_count
        new_remains = payload.remains if payload.remains is not None else existing.remains
        new_prov_ord = payload.provider_order_id if payload.provider_order_id is not None else existing.provider_order_id
        now_iso = utc_now().isoformat()

        # Handle financial refund side-effects
        if new_status in (OrderStatus.CANCELLED, OrderStatus.REFUNDED) and existing.status not in (OrderStatus.CANCELLED, OrderStatus.REFUNDED):
            # Full refund
            await self.adjust_user_balance(
                existing.user_id,
                existing.charge_usd,
                TransactionType.REFUND,
                f"Full refund for cancelled Order #{order_id}",
            )
        elif new_status == OrderStatus.PARTIAL and existing.status != OrderStatus.PARTIAL:
            # Partial refund proportional to remains
            if existing.quantity > 0 and new_remains > 0:
                refund_ratio = min(1.0, max(0.0, new_remains / existing.quantity))
                refund_amount = round(existing.charge_usd * refund_ratio, 4)
                if refund_amount > 0:
                    await self.adjust_user_balance(
                        existing.user_id,
                        refund_amount,
                        TransactionType.REFUND,
                        f"Partial refund ({new_remains} remains) for Order #{order_id}",
                    )

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                UPDATE orders SET status = ?, start_count = ?, remains = ?, provider_order_id = ?, updated_at = ?
                WHERE id = ?
                """,
                (new_status.value, new_start, new_remains, new_prov_ord, now_iso, order_id),
            )
            await db.commit()

        return await self.get_order_by_id(order_id)

    # --- Analytics & Dashboard ---
    async def get_dashboard_metrics(self) -> SmmDashboardMetrics:
        async with aiosqlite.connect(self.db_path) as db:
            # Order counts and financials
            cursor = await db.execute(
                """
                SELECT
                    COUNT(*),
                    COALESCE(SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN status IN ('pending', 'in_progress', 'processing') THEN 1 ELSE 0 END), 0),
                    COALESCE(SUM(charge_usd), 0.0),
                    COALESCE(SUM(provider_cost_usd), 0.0)
                FROM orders
                """
            )
            ord_row = await cursor.fetchone()
            total_orders = ord_row[0]
            completed = ord_row[1]
            pending = ord_row[2]
            total_rev = round(ord_row[3], 2)
            total_cost = round(ord_row[4], 2)
            gross_profit = round(total_rev - total_cost, 2)
            profit_margin = round((gross_profit / total_rev * 100.0), 1) if total_rev > 0 else 0.0

            # Users & services counts
            u_cur = await db.execute("SELECT COUNT(*) FROM users")
            total_users = (await u_cur.fetchone())[0]

            s_cur = await db.execute("SELECT COUNT(*) FROM services")
            total_services = (await s_cur.fetchone())[0]

            # Platform breakdown
            p_cur = await db.execute(
                """
                SELECT s.platform, COUNT(o.id), COALESCE(SUM(o.charge_usd), 0.0)
                FROM services s
                LEFT JOIN orders o ON o.service_id = s.id
                GROUP BY s.platform
                """
            )
            p_rows = await p_cur.fetchall()
            platforms = [
                PlatformMetric(platform=r[0], order_count=r[1], revenue_usd=round(r[2], 2))
                for r in p_rows
            ]

            return SmmDashboardMetrics(
                total_orders=total_orders,
                completed_orders=completed,
                pending_orders=pending,
                total_revenue_usd=total_rev,
                total_provider_cost_usd=total_cost,
                gross_profit_usd=gross_profit,
                profit_margin_percent=profit_margin,
                total_users=total_users,
                total_services=total_services,
                platform_breakdown=platforms,
            )
