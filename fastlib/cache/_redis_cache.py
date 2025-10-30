# SPDX-License-Identifier: MIT
"""Redis cache implementation"""

import asyncio
from typing import Optional

from loguru import logger

from fastlib import ConfigManager

try:
    import redis.asyncio as redis
except ModuleNotFoundError:
    logger.warning(
        "Cannot find redis module, please install it via `uv add redis[hiredis]`"
    )
    redis = None
    RedisError = Exception
except Exception:
    logger.error("Error importing redis module")
    redis = None
    RedisError = Exception


class RedisCacheManager:
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
                    database_config = ConfigManager.get_database_config()
                    cls._connection_pool = redis.ConnectionPool.from_url(
                        f"redis://:{database_config.cache_pass}@{database_config.cache_host}:{database_config.cache_port}/{database_config.db_num}",
                        decode_responses=True,
                    )
                if cls._instance is None:
                    cls._instance = redis.Redis(connection_pool=cls._connection_pool)
        return cls._instance

    @classmethod
    async def close_pool(cls):
        """Close the connection pool."""
        if cls._connection_pool:
            await cls._connection_pool.disconnect()
            cls._connection_pool = None
            cls._instance = None
