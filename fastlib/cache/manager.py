# SPDX-License-Identifier: MIT
"""Cache Client manager to instantiate the appropriate cache client"""

from fastlib.config.manager import ConfigManager


async def get_cache_client():
    """Initialize and return the appropriate cache client based on configuration.

    Returns:
        Cache: Redis client if Redis is enabled in config, otherwise returns FakeRedis client.
    """
    config = ConfigManager.get_database_config()

    if config.enable_redis:
        from fastlib.cache._redis_cache import RedisManager

        redis_client = await RedisManager.get_instance()
        return redis_client
    else:
        from fastlib.cache._memony_cache import MemoryCacheManager

        fake_client = await MemoryCacheManager.get_instance()
        return fake_client
