# SPDX-License-Identifier: MIT
"""Cache Client manager to instantiate the appropriate cache client"""

from fastlib.cache.base import Cache
from fastlib.config.manager import ConfigManager


async def get_cache_client() -> Cache:
    """Initialize and return the appropriate cache client based on configuration.

    Returns:
        Cache: Redis client if Redis is enabled in config, otherwise returns page cache.
    """
    config = ConfigManager.get_database_config()
    if config.enable_redis:
        from fastlib.cache._redis_cache import RedisCache, RedisManager

        redis_client = await RedisManager.get_instance()
        return RedisCache(redis_client)
    else:
        from fastlib.cache._memony_cache import MemoryCache

        return MemoryCache()
