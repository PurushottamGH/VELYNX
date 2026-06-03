"""Redis caching layer — session state, hot memory, reflection cache."""
from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger("uvicorn")

_DEFAULT_TTL = 3600  # 1 hour


class RedisCache:
    """Async Redis cache wrapper with graceful degradation."""

    def __init__(self) -> None:
        self._client = None
        self._available = False

    async def initialize(self, redis_url: str | None = None) -> None:
        """Connect to Redis. No-op if URL is None."""
        if not redis_url:
            return
        try:
            import redis.asyncio as aioredis
            self._client = aioredis.from_url(redis_url, decode_responses=True)
            await self._client.ping()
            self._available = True
            logger.info("Redis cache connected")
        except Exception as exc:
            logger.warning("Redis cache unavailable: %s", exc)
            self._available = False

    @property
    def available(self) -> bool:
        return self._available

    async def get(self, key: str) -> Any | None:
        if not self._available:
            return None
        try:
            raw = await self._client.get(key)
            return json.loads(raw) if raw else None
        except Exception:
            return None

    async def set(self, key: str, value: Any, ttl: int = _DEFAULT_TTL) -> None:
        if not self._available:
            return
        try:
            await self._client.set(key, json.dumps(value, default=str), ex=ttl)
        except Exception:
            pass

    async def delete(self, key: str) -> None:
        if not self._available:
            return
        try:
            await self._client.delete(key)
        except Exception:
            pass

    async def incr(self, key: str) -> int | None:
        if not self._available:
            return None
        try:
            return await self._client.incr(key)
        except Exception:
            return None

    async def keys(self, pattern: str = "*") -> list[str]:
        if not self._available:
            return []
        try:
            return await self._client.keys(pattern)
        except Exception:
            return []

    async def publish(self, channel: str, message: str) -> None:
        """Publish a message to a Redis pub/sub channel."""
        if not self._available:
            return
        try:
            await self._client.publish(channel, message)
        except Exception:
            pass

    async def subscribe(self, *channels: str):
        """Create a pub/sub subscription. Returns the pubsub object or None."""
        if not self._available:
            return None
        try:
            pubsub = self._client.pubsub()
            await pubsub.subscribe(*channels)
            return pubsub
        except Exception:
            return None

    async def close(self) -> None:
        if self._client:
            await self._client.close()


# Module-level singleton
redis_cache = RedisCache()
