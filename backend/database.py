import aiosqlite
from typing import AsyncGenerator

DB_PATH = "f1sid.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS prediction_rooms (
                code        TEXT PRIMARY KEY,
                race_name   TEXT NOT NULL,
                race_round  INTEGER NOT NULL,
                season      INTEGER NOT NULL,
                locked      INTEGER DEFAULT 0,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                room_code     TEXT NOT NULL,
                username      TEXT NOT NULL,
                p1            TEXT NOT NULL,
                p2            TEXT NOT NULL,
                p3            TEXT NOT NULL,
                fastest_lap   TEXT,
                score         INTEGER DEFAULT 0,
                submitted_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_code) REFERENCES prediction_rooms(code),
                UNIQUE(room_code, username)
            )
        """)
        # Analytics cache: stores serialised JSON blobs keyed by cache_key
        await db.execute("""
            CREATE TABLE IF NOT EXISTS analytics_cache (
                cache_key   TEXT PRIMARY KEY,
                payload     TEXT NOT NULL,
                cached_at   REAL NOT NULL
            )
        """)
        # Jolpica result cache: faster repeated API calls
        await db.execute("""
            CREATE TABLE IF NOT EXISTS api_cache (
                path        TEXT PRIMARY KEY,
                payload     TEXT NOT NULL,
                cached_at   REAL NOT NULL,
                ttl         INTEGER NOT NULL DEFAULT 3600
            )
        """)
        await db.commit()


async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db
