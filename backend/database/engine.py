"""Async SQLAlchemy engine, session factory, and Redis client."""
from __future__ import annotations

import logging
import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

logger = logging.getLogger("uvicorn")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://velynx:velynx@localhost:5432/velynx",
)

# Test override: use SQLite if VELYNX_TEST_DB=1
if os.getenv("VELYNX_TEST_DB"):
    DATABASE_URL = "sqlite+aiosqlite:///./test_velynx.db"

async_engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False,
)

async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    """Dependency-injectable async session."""
    async with async_session() as session:
        yield session


# Redis client (lazy init)
_redis_client = None


async def get_redis():
    """Get or create the async Redis client."""
    global _redis_client
    if _redis_client is None:
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            return None
        try:
            import redis.asyncio as aioredis
            _redis_client = aioredis.from_url(redis_url, decode_responses=True)
            await _redis_client.ping()
            logger.info("Redis connected: %s", redis_url)
        except Exception as exc:
            logger.warning("Redis unavailable: %s", exc)
            _redis_client = None
    return _redis_client
