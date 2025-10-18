# SPDX-License-Identifier: MIT
"""Memory-based cache implementation compatible with Cache interface."""

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Any

from fastlib.cache.base import Cache, CacheError


class MemoryCache(Cache):
    """
    Memory-based cache implementation
    """

    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        self._data: dict[str, Any] = {}
        self._expiry: dict[str, float] = {}
        self._lists: dict[str, list] = {}
        self._sets: dict[str, set] = {}
        self._hashes: dict[str, dict[str, Any]] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()

    def _is_expired(self, key: str) -> bool:
        """Check if a key has expired"""
        if key not in self._expiry:
            return False
        return time.time() > self._expiry[key]

    def _clean_expired(self):
        """Clean up expired keys"""
        expired_keys = [k for k in self._expiry if self._is_expired(k)]
        for key in expired_keys:
            self._data.pop(key, None)
            self._expiry.pop(key, None)
            self._lists.pop(key, None)
            self._sets.pop(key, None)
            self._hashes.pop(key, None)

    async def ping(self) -> bool:
        try:
            await self.set("__ping__", "pong", ex=1)
            return True
        except Exception as e:
            raise CacheError("Ping failed", e) from e

    async def set(
        self,
        key: str,
        value: Any,
        ex: int | None = None,
        nx: bool = False,  # only set if not exists
        xx: bool = False,  # only set if exists
    ) -> bool:
        async with self._global_lock:
            self._clean_expired()

            if nx and key in self._data:
                return False
            if xx and key not in self._data:
                return False

            self._data[key] = value
            if ex is not None:
                self._expiry[key] = time.time() + ex
            elif key in self._expiry:
                del self._expiry[key]  # Remove expiration time

            return True

    async def get(self, key: str) -> Any | None:
        async with self._global_lock:
            self._clean_expired()

            if key in self._data and not self._is_expired(key):
                return self._data[key]
            return None

    async def delete(self, *keys: str) -> int:
        async with self._global_lock:
            count = 0
            for key in keys:
                if key in self._data:
                    del self._data[key]
                    self._expiry.pop(key, None)
                    self._lists.pop(key, None)
                    self._sets.pop(key, None)
                    self._hashes.pop(key, None)
                    count += 1
            return count

    async def exists(self, *keys: str) -> int:
        async with self._global_lock:
            self._clean_expired()
            return sum(1 for k in keys if k in self._data and not self._is_expired(k))

    async def expire(self, key: str, seconds: int) -> bool:
        async with self._global_lock:
            if key not in self._data or self._is_expired(key):
                return False
            self._expiry[key] = time.time() + seconds
            return True

    async def ttl(self, key: str) -> int:
        async with self._global_lock:
            if key not in self._data or key not in self._expiry:
                return -1  # No expiration time set
            if self._is_expired(key):
                return -2  # Key does not exist (expired)
            return int(self._expiry[key] - time.time())

    async def incr(self, key: str, amount: int = 1) -> int:
        async with self._global_lock:
            self._clean_expired()

            current = self._data.get(key, 0)
            if not isinstance(current, int):
                raise CacheError("Value is not integer")

            new_value = current + amount
            self._data[key] = new_value
            return new_value

    async def decr(self, key: str, amount: int = 1) -> int:
        return await self.incr(key, -amount)

    # ---------------- Hash (dict) ----------------
    async def hset(self, name: str, key: str, value: Any) -> int:
        async with self._global_lock:
            if name not in self._hashes:
                self._hashes[name] = {}
            self._hashes[name][key] = value
            return 1

    async def hget(self, name: str, key: str) -> Any | None:
        async with self._global_lock:
            if name in self._hashes:
                return self._hashes[name].get(key)
            return None

    async def hgetall(self, name: str) -> dict[str, Any]:
        async with self._global_lock:
            return self._hashes.get(name, {}).copy()

    async def hdel(self, name: str, *keys: str) -> int:
        async with self._global_lock:
            if name not in self._hashes:
                return 0
            removed = 0
            for k in keys:
                if k in self._hashes[name]:
                    del self._hashes[name][k]
                    removed += 1
            return removed

    # ---------------- List ----------------
    async def lpush(self, name: str, *values: Any) -> int:
        async with self._global_lock:
            if name not in self._lists:
                self._lists[name] = []
            self._lists[name][:0] = values  # Insert at the beginning
            return len(self._lists[name])

    async def rpush(self, name: str, *values: Any) -> int:
        async with self._global_lock:
            if name not in self._lists:
                self._lists[name] = []
            self._lists[name].extend(values)
            return len(self._lists[name])

    async def lpop(self, name: str) -> Any | None:
        async with self._global_lock:
            if name not in self._lists or not self._lists[name]:
                return None
            return self._lists[name].pop(0)

    async def rpop(self, name: str) -> Any | None:
        async with self._global_lock:
            if name not in self._lists or not self._lists[name]:
                return None
            return self._lists[name].pop()

    async def lrange(self, name: str, start: int = 0, end: int = -1) -> list[Any]:
        async with self._global_lock:
            if name not in self._lists:
                return []
            lst = self._lists[name]
            if end == -1:
                end = len(lst)
            return lst[start:end]

    # ---------------- Set ----------------
    async def sadd(self, name: str, *values: Any) -> int:
        async with self._global_lock:
            if name not in self._sets:
                self._sets[name] = set()
            before = len(self._sets[name])
            self._sets[name].update(values)
            return len(self._sets[name]) - before

    async def smembers(self, name: str) -> list[Any]:
        async with self._global_lock:
            if name not in self._sets:
                return []
            return list(self._sets[name])

    async def srem(self, name: str, *values: Any) -> int:
        async with self._global_lock:
            if name not in self._sets:
                return 0
            before = len(self._sets[name])
            for v in values:
                self._sets[name].discard(v)
            return before - len(self._sets[name])

    # ---------------- Lock (async-based) ----------------
    async def acquire_lock(
        self,
        lock_name: str,
        timeout: int = 10,
        blocking_timeout: int = 5,
        thread_local: bool = True,
    ) -> bool:
        if lock_name not in self._locks:
            self._locks[lock_name] = asyncio.Lock()

        try:
            await asyncio.wait_for(
                self._locks[lock_name].acquire(), timeout=blocking_timeout
            )
            return True
        except asyncio.TimeoutError:
            return False

    async def release_lock(self, lock_name: str) -> bool:
        if lock_name in self._locks and self._locks[lock_name].locked():
            self._locks[lock_name].release()
            return True
        return False

    @asynccontextmanager
    async def lock(self, lock_name: str, timeout: int = 10, blocking_timeout: int = 5):
        acquired = await self.acquire_lock(lock_name, timeout, blocking_timeout)
        if not acquired:
            raise CacheError(f"Failed to acquire lock: {lock_name}")
        try:
            yield
        finally:
            await self.release_lock(lock_name)

    async def close(self) -> None:
        """Clean up resources"""
        self._data.clear()
        self._expiry.clear()
        self._lists.clear()
        self._sets.clear()
        self._hashes.clear()
        self._locks.clear()

    def clear(self) -> None:
        """Clear all cached data"""
        self._data.clear()
        self._expiry.clear()
        self._lists.clear()
        self._sets.clear()
        self._hashes.clear()
