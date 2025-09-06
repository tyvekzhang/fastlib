"""
Base cache interface providing a unified caching abstraction.

This module defines the base Cache class that provides a common interface
for different caching implementations like Redis, memory cache, etc.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager


class CacheError(Exception):
    """Custom exception for cache-related errors."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.message = message
        self.original_error = original_error
        super().__init__(f"Cache Error: {message}")


class Cache(ABC):
    """
    Abstract base class for cache implementations.
    
    This class defines the interface that all cache implementations must follow,
    providing a unified API for caching operations across different backends.
    """

    @abstractmethod
    async def ping(self) -> bool:
        """Test cache connection/availability."""
        pass

    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ex: Optional[int] = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        """Set a key-value pair in cache."""
        pass

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        pass

    @abstractmethod
    async def delete(self, *keys: str) -> int:
        """Delete one or more keys from cache."""
        pass

    @abstractmethod
    async def exists(self, *keys: str) -> int:
        """Check if keys exist in cache."""
        pass

    @abstractmethod
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration time for a key."""
        pass

    @abstractmethod
    async def ttl(self, key: str) -> int:
        """Get time to live for a key."""
        pass

    @abstractmethod
    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment a counter in cache."""
        pass

    @abstractmethod
    async def decr(self, key: str, amount: int = 1) -> int:
        """Decrement a counter in cache."""
        pass

    @abstractmethod
    async def hset(self, name: str, key: str, value: Any) -> int:
        """Set a field in a hash."""
        pass

    @abstractmethod
    async def hget(self, name: str, key: str) -> Optional[Any]:
        """Get a field from a hash."""
        pass

    @abstractmethod
    async def hgetall(self, name: str) -> Dict[str, Any]:
        """Get all fields from a hash."""
        pass

    @abstractmethod
    async def hdel(self, name: str, *keys: str) -> int:
        """Delete fields from a hash."""
        pass

    @abstractmethod
    async def lpush(self, name: str, *values: Any) -> int:
        """Push values to the left of a list."""
        pass

    @abstractmethod
    async def rpush(self, name: str, *values: Any) -> int:
        """Push values to the right of a list."""
        pass

    @abstractmethod
    async def lpop(self, name: str) -> Optional[Any]:
        """Pop a value from the left of a list."""
        pass

    @abstractmethod
    async def rpop(self, name: str) -> Optional[Any]:
        """Pop a value from the right of a list."""
        pass

    @abstractmethod
    async def lrange(self, name: str, start: int = 0, end: int = -1) -> List[Any]:
        """Get a range of values from a list."""
        pass

    @abstractmethod
    async def sadd(self, name: str, *values: Any) -> int:
        """Add values to a set."""
        pass

    @abstractmethod
    async def smembers(self, name: str) -> List[Any]:
        """Get all members of a set."""
        pass

    @abstractmethod
    async def srem(self, name: str, *values: Any) -> int:
        """Remove values from a set."""
        pass

    @abstractmethod
    async def acquire_lock(
        self,
        lock_name: str,
        timeout: int = 10,
        blocking_timeout: int = 5,
        thread_local: bool = True,
    ) -> bool:
        """Acquire a distributed lock."""
        pass

    @abstractmethod
    async def release_lock(self, lock_name: str) -> bool:
        """Release a distributed lock."""
        pass

    @abstractmethod
    @asynccontextmanager
    async def lock(self, lock_name: str, timeout: int = 10, blocking_timeout: int = 5):
        """Context manager for distributed locks."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close cache connections."""
        pass

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()