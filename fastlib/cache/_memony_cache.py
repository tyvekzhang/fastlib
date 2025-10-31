# SPDX-License-Identifier: MIT
"""Memory (MemoryStorage) Cache Manager for in-memory caching"""

import asyncio


class MemoryStorage:
    """In-memory storage implementation"""

    def __init__(self):
        self._data = {}

    async def set(self, key, value):
        self._data[key] = value
        return key

    async def get(self, key):
        return self._data.get(key)

    async def update(self, key, **updated):
        if key not in self._data:
            return None

        value = self._data[key]
        for key, value in updated.items():
            if hasattr(value, key):
                setattr(value, key, value)

        return value

    async def delete(self, key):
        if key in self._data:
            del self._data[key]
            return True
        return False

    async def list(self):
        return list(self._data.values())


class MemoryCacheManager:
    """Singleton manager for in-memory (MemoryStorage) cache client."""

    _instance = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_instance(cls):
        """Get a singleton MemoryStorage instance."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = MemoryStorage()
        return cls._instance

    @classmethod
    async def close(cls):
        """Close the MemoryStorage instance (for cleanup in tests)."""
        if cls._instance is not None:
            await cls._instance.close()
            cls._instance = None

    @classmethod
    async def reset(cls):
        """Clear all cached data without destroying the instance."""
        if cls._instance is not None:
            await cls._instance.flushall()
