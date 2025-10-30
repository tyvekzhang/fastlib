# SPDX-License-Identifier: MIT
"""Memory (FakeRedis) Cache Manager for in-memory caching"""

import asyncio

from fakeredis.aioredis import FakeRedis


class MemoryCacheManager:
    """Singleton manager for in-memory (FakeRedis) cache client."""

    _instance: FakeRedis | None = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_instance(cls) -> FakeRedis:
        """Get a singleton FakeRedis instance."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = FakeRedis()
        return cls._instance

    @classmethod
    async def close(cls):
        """Close the FakeRedis instance (for cleanup in tests)."""
        if cls._instance is not None:
            await cls._instance.close()
            cls._instance = None

    @classmethod
    async def reset(cls):
        """Clear all cached data without destroying the instance."""
        if cls._instance is not None:
            await cls._instance.flushall()
