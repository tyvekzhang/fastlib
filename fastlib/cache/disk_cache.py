# SPDX-License-Identifier: MIT
"""DiskCache-based PageCache implementation compatible with Cache interface."""

from contextlib import asynccontextmanager
import json
import time
import threading
from typing import Any, Dict, List, Optional, Union
import diskcache

from fastlib.cache.base_cache import Cache, CacheError


class PageCache(Cache):
    def __init__(self, directory: str = "./.diskcache"):
        self.cache = diskcache.Cache(directory)
        self._locks: Dict[str, threading.Lock] = {}

    async def ping(self) -> bool:
        try:
            self.cache.set("__ping__", "pong", expire=1)
            return True
        except Exception as e:
            raise CacheError("Ping failed", e)

    async def set(
        self,
        key: str,
        value: Any,
        ex: Optional[int] = None,
        nx: bool = False,  # only set if not exists
        xx: bool = False,  # only set if exists
    ) -> bool:
        if nx and key in self.cache:
            return False
        if xx and key not in self.cache:
            return False
        return self.cache.set(key, value, expire=ex)

    async def get(self, key: str) -> Optional[Any]:
        return self.cache.get(key, None)

    async def delete(self, *keys: str) -> int:
        count = 0
        for k in keys:
            if k in self.cache:
                self.cache.delete(k)
                count += 1
        return count

    async def exists(self, *keys: str) -> int:
        return sum(1 for k in keys if k in self.cache)

    async def expire(self, key: str, seconds: int) -> bool:
        if key not in self.cache:
            return False
        value = self.cache.get(key)
        self.cache.set(key, value, expire=seconds)
        return True

    async def ttl(self, key: str) -> int:
        if key not in self.cache:
            return -2  # Redis convention: -2 means key does not exist
        expiry = self.cache.ttl(key)
        return int(expiry) if expiry is not None else -1  # -1 means no expiry

    async def incr(self, key: str, amount: int = 1) -> int:
        with self.cache.transact():
            val = self.cache.get(key, 0)
            if not isinstance(val, int):
                raise CacheError("Value is not integer")
            val += amount
            self.cache.set(key, val)
            return val

    async def decr(self, key: str, amount: int = 1) -> int:
        return await self.incr(key, -amount)

    # ---------------- Hash (dict) ----------------
    async def hset(self, name: str, key: str, value: Any) -> int:
        data = self.cache.get(name, {})
        if not isinstance(data, dict):
            data = {}
        data[key] = value
        self.cache.set(name, data)
        return 1

    async def hget(self, name: str, key: str) -> Optional[Any]:
        data = self.cache.get(name, {})
        return data.get(key) if isinstance(data, dict) else None

    async def hgetall(self, name: str) -> Dict[str, Any]:
        data = self.cache.get(name, {})
        return data if isinstance(data, dict) else {}

    async def hdel(self, name: str, *keys: str) -> int:
        data = self.cache.get(name, {})
        if not isinstance(data, dict):
            return 0
        removed = 0
        for k in keys:
            if k in data:
                del data[k]
                removed += 1
        self.cache.set(name, data)
        return removed

    # ---------------- List ----------------
    def _get_list(self, key: str) -> List[Any]:
        data = self.cache.get(key)
        if data is None:
            return []
        if isinstance(data, str):  # if JSON stored
            try:
                return json.loads(data)
            except Exception:
                return []
        if isinstance(data, list):
            return data
        return []

    def _set_list(self, key: str, value: List[Any]):
        self.cache.set(key, json.dumps(value))

    async def lpush(self, name: str, *values: Any) -> int:
        lst = self._get_list(name)
        for v in values:
            lst.insert(0, v)
        self._set_list(name, lst)
        return len(lst)

    async def rpush(self, name: str, *values: Any) -> int:
        lst = self._get_list(name)
        lst.extend(values)
        self._set_list(name, lst)
        return len(lst)

    async def lpop(self, name: str) -> Optional[Any]:
        lst = self._get_list(name)
        if not lst:
            return None
        val = lst.pop(0)
        self._set_list(name, lst)
        return val

    async def rpop(self, name: str) -> Optional[Any]:
        lst = self._get_list(name)
        if not lst:
            return None
        val = lst.pop()
        self._set_list(name, lst)
        return val

    async def lrange(self, name: str, start: int = 0, end: int = -1) -> List[Any]:
        lst = self._get_list(name)
        if end == -1:
            end = len(lst) - 1
        return lst[start : end + 1]

    # ---------------- Set ----------------
    async def sadd(self, name: str, *values: Any) -> int:
        current = self.cache.get(name, set())
        if not isinstance(current, set):
            current = set()
        before = len(current)
        current.update(values)
        self.cache.set(name, current)
        return len(current) - before

    async def smembers(self, name: str) -> List[Any]:
        current = self.cache.get(name, set())
        return list(current) if isinstance(current, set) else []

    async def srem(self, name: str, *values: Any) -> int:
        current = self.cache.get(name, set())
        if not isinstance(current, set):
            return 0
        before = len(current)
        for v in values:
            current.discard(v)
        self.cache.set(name, current)
        return before - len(current)

    # ---------------- Lock (simple thread-based) ----------------
    async def acquire_lock(
        self, lock_name: str, timeout: int = 10, blocking_timeout: int = 5, thread_local: bool = True
    ) -> bool:
        lock = self._locks.setdefault(lock_name, threading.Lock())
        start = time.time()
        while time.time() - start < blocking_timeout:
            if lock.acquire(blocking=False):
                return True
            time.sleep(0.05)
        return False

    async def release_lock(self, lock_name: str) -> bool:
        lock = self._locks.get(lock_name)
        if lock and lock.locked():
            lock.release()
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
        self.cache.close()