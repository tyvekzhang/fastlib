# SPDX-License-Identifier: MIT
"""Redis cache implementation"""

import asyncio
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union

from loguru import logger

from fastlib.cache.base_cache import Cache, CacheError

try:
    import redis.asyncio as redis
    from redis.exceptions import RedisError
except ModuleNotFoundError:
    logger.error(
        "Cannot find redis module, please install it via `uv add redis[hiredis] and then uv remove diskcache`"
    )
    redis = None
    RedisError = Exception
except Exception:
    logger.error("Error importing redis module")
    redis = None
    RedisError = Exception

from fastlib.config.manager import load_config


class RedisCache(Cache):
    def __init__(self, redis_client):
        if redis is None:
            raise RuntimeError(
                "Redis module is not available. Please install it via 'uv add redis[hiredis]'"
            )
        self.redis_client = redis_client
        self._lock_tokens = {}  # Store lock tokens for distributed locks

    async def ping(self) -> bool:
        """Test cache connection/availability."""
        try:
            return await self.redis_client.ping()
        except RedisError as e:
            raise CacheError("Redis ping failed", e)

    async def set(
        self,
        key: str,
        value: Any,
        ex: Optional[int] = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        """Set a key-value pair in cache."""
        try:
            if nx and xx:
                raise ValueError("Cannot use both nx and xx options together")
            
            if nx:
                return await self.redis_client.set(key, value, ex=ex, nx=True)
            elif xx:
                return await self.redis_client.set(key, value, ex=ex, xx=True)
            else:
                return await self.redis_client.set(key, value, ex=ex)
        except RedisError as e:
            raise CacheError(f"Failed to set key {key}", e)

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        try:
            return await self.redis_client.get(key)
        except RedisError as e:
            raise CacheError(f"Failed to get key {key}", e)

    async def delete(self, *keys: str) -> int:
        """Delete one or more keys from cache."""
        try:
            return await self.redis_client.delete(*keys)
        except RedisError as e:
            raise CacheError(f"Failed to delete keys {keys}", e)

    async def exists(self, *keys: str) -> int:
        """Check if keys exist in cache."""
        try:
            return await self.redis_client.exists(*keys)
        except RedisError as e:
            raise CacheError(f"Failed to check existence of keys {keys}", e)

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration time for a key."""
        try:
            return await self.redis_client.expire(key, seconds)
        except RedisError as e:
            raise CacheError(f"Failed to set expiration for key {key}", e)

    async def ttl(self, key: str) -> int:
        """Get time to live for a key."""
        try:
            return await self.redis_client.ttl(key)
        except RedisError as e:
            raise CacheError(f"Failed to get TTL for key {key}", e)

    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment a counter in cache."""
        try:
            if amount == 1:
                return await self.redis_client.incr(key)
            else:
                return await self.redis_client.incrby(key, amount)
        except RedisError as e:
            raise CacheError(f"Failed to increment key {key}", e)

    async def decr(self, key: str, amount: int = 1) -> int:
        """Decrement a counter in cache."""
        try:
            if amount == 1:
                return await self.redis_client.decr(key)
            else:
                return await self.redis_client.decrby(key, amount)
        except RedisError as e:
            raise CacheError(f"Failed to decrement key {key}", e)

    async def hset(self, name: str, key: str, value: Any) -> int:
        """Set a field in a hash."""
        try:
            return await self.redis_client.hset(name, key, value)
        except RedisError as e:
            raise CacheError(f"Failed to set hash field {key} in {name}", e)

    async def hget(self, name: str, key: str) -> Optional[Any]:
        """Get a field from a hash."""
        try:
            return await self.redis_client.hget(name, key)
        except RedisError as e:
            raise CacheError(f"Failed to get hash field {key} from {name}", e)

    async def hgetall(self, name: str) -> Dict[str, Any]:
        """Get all fields from a hash."""
        try:
            return await self.redis_client.hgetall(name)
        except RedisError as e:
            raise CacheError(f"Failed to get all hash fields from {name}", e)

    async def hdel(self, name: str, *keys: str) -> int:
        """Delete fields from a hash."""
        try:
            return await self.redis_client.hdel(name, *keys)
        except RedisError as e:
            raise CacheError(f"Failed to delete hash fields {keys} from {name}", e)

    async def lpush(self, name: str, *values: Any) -> int:
        """Push values to the left of a list."""
        try:
            return await self.redis_client.lpush(name, *values)
        except RedisError as e:
            raise CacheError(f"Failed to lpush values to list {name}", e)

    async def rpush(self, name: str, *values: Any) -> int:
        """Push values to the right of a list."""
        try:
            return await self.redis_client.rpush(name, *values)
        except RedisError as e:
            raise CacheError(f"Failed to rpush values to list {name}", e)

    async def lpop(self, name: str) -> Optional[Any]:
        """Pop a value from the left of a list."""
        try:
            return await self.redis_client.lpop(name)
        except RedisError as e:
            raise CacheError(f"Failed to lpop from list {name}", e)

    async def rpop(self, name: str) -> Optional[Any]:
        """Pop a value from the right of a list."""
        try:
            return await self.redis_client.rpop(name)
        except RedisError as e:
            raise CacheError(f"Failed to rpop from list {name}", e)

    async def lrange(self, name: str, start: int = 0, end: int = -1) -> List[Any]:
        """Get a range of values from a list."""
        try:
            return await self.redis_client.lrange(name, start, end)
        except RedisError as e:
            raise CacheError(f"Failed to get range from list {name}", e)

    async def sadd(self, name: str, *values: Any) -> int:
        """Add values to a set."""
        try:
            return await self.redis_client.sadd(name, *values)
        except RedisError as e:
            raise CacheError(f"Failed to add values to set {name}", e)

    async def smembers(self, name: str) -> List[Any]:
        """Get all members of a set."""
        try:
            return await self.redis_client.smembers(name)
        except RedisError as e:
            raise CacheError(f"Failed to get members from set {name}", e)

    async def srem(self, name: str, *values: Any) -> int:
        """Remove values from a set."""
        try:
            return await self.redis_client.srem(name, *values)
        except RedisError as e:
            raise CacheError(f"Failed to remove values from set {name}", e)

    async def acquire_lock(
        self,
        lock_name: str,
        timeout: int = 10,
        blocking_timeout: int = 5,
        thread_local: bool = True,
    ) -> bool:
        """Acquire a distributed lock."""
        try:
            # Generate a unique identifier for this lock
            identifier = str(uuid.uuid4())
            
            # Calculate the end time for blocking
            end_time = time.time() + blocking_timeout
            
            while time.time() < end_time:
                # Try to acquire the lock
                acquired = await self.redis_client.set(
                    lock_name, identifier, ex=timeout, nx=True
                )
                
                if acquired:
                    # Store the identifier for later release
                    self._lock_tokens[lock_name] = identifier
                    return True
                
                # Wait a bit before trying again
                await asyncio.sleep(0.1)
            
            return False
        except RedisError as e:
            raise CacheError(f"Failed to acquire lock {lock_name}", e)

    async def release_lock(self, lock_name: str) -> bool:
        """Release a distributed lock."""
        try:
            # Check if we have the lock
            if lock_name not in self._lock_tokens:
                return False
            
            # Use a Lua script to ensure atomic check and delete
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            
            result = await self.redis_client.eval(
                lua_script, 1, lock_name, self._lock_tokens[lock_name]
            )
            
            # Remove the token from our storage
            if result:
                del self._lock_tokens[lock_name]
            
            return bool(result)
        except RedisError as e:
            raise CacheError(f"Failed to release lock {lock_name}", e)

    @asynccontextmanager
    async def lock(self, lock_name: str, timeout: int = 10, blocking_timeout: int = 5):
        """Context manager for distributed locks."""
        acquired = False
        try:
            acquired = await self.acquire_lock(lock_name, timeout, blocking_timeout)
            if not acquired:
                raise CacheError(f"Failed to acquire lock {lock_name} within timeout")
            yield
        finally:
            if acquired:
                await self.release_lock(lock_name)

    async def close(self) -> None:
        """Close cache connections."""
        try:
            await self.redis_client.close()
        except RedisError as e:
            raise CacheError("Failed to close Redis connection", e)

    # Additional methods from existing implementation that are not in the interface
    async def llen(self, key: str) -> int:
        """Get the length of a list."""
        try:
            return await self.redis_client.llen(key)
        except RedisError as e:
            raise CacheError(f"Failed to get length of list {key}", e)

    async def lindex(self, key: str, index: int) -> Any:
        """Get an element from a list by its index."""
        try:
            return await self.redis_client.lindex(key, index)
        except RedisError as e:
            raise CacheError(f"Failed to get index {index} from list {key}", e)

    async def lset(self, key: str, index: int, value: Any) -> bool:
        """Set the value of an element in a list by its index."""
        try:
            await self.redis_client.lset(key, index, value)
            return True
        except RedisError as e:
            raise CacheError(f"Failed to set index {index} in list {key}", e)
            return False

    async def lrem(self, key: str, count: int, value: Any) -> int:
        """Remove elements from a list."""
        try:
            return await self.redis_client.lrem(key, count, value)
        except RedisError as e:
            raise CacheError(f"Failed to remove elements from list {key}", e)

    async def ltrim(self, key: str, start: int, end: int) -> bool:
        """Trim a list to the specified range."""
        try:
            await self.redis_client.ltrim(key, start, end)
            return True
        except RedisError as e:
            raise CacheError(f"Failed to trim list {key}", e)
            return False


class RedisManager:
    _instance: Optional["redis.Redis"] = None
    _connection_pool: Optional["redis.ConnectionPool"] = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_instance(cls) -> "redis.Redis":
        """
        Get redis instance
        """
        if redis is None:
            raise RuntimeError(
                "Redis module is not available. Please install it via 'uv add redis[hiredis]'"
            )

        if cls._instance is None:
            async with cls._lock:
                if cls._connection_pool is None:
                    database = load_config().database
                    cls._connection_pool = redis.ConnectionPool.from_url(
                        f"redis://:{database.cache_pass}@{database.cache_host}:{database.cache_port}/{database.db_num}",
                        decode_responses=True,
                    )
                if cls._instance is None:
                    cls._instance = redis.Redis(connection_pool=cls._connection_pool)
        return cls._instance

    @classmethod
    async def get_cache(cls) -> RedisCache:
        """Get a RedisCache instance."""
        redis_client = await cls.get_instance()
        return RedisCache(redis_client)

    @classmethod
    async def close_pool(cls):
        """Close the connection pool."""
        if cls._connection_pool:
            await cls._connection_pool.disconnect()
            cls._connection_pool = None
            cls._instance = None