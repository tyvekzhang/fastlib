# SPDX-License-Identifier: MIT
"""Redis cache implementation"""

import asyncio
import json
from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel
from redis._parsers.encoders import Encoder

from fastlib import ConfigManager
from fastlib.logging.handlers import logger

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


class CustomJsonEncoder(Encoder):
    def encode(self, value: Any):
        """Extended encoding to support datetime and Pydantic models."""
        if isinstance(value, datetime | date):
            return json.dumps(
                {
                    "__type__": "datetime",
                    "value": value.isoformat(),
                }
            ).encode("utf-8")

        elif isinstance(value, BaseModel):
            return json.dumps(
                {
                    "__type__": "pydantic",
                    "model": value.__class__.__name__,
                    "module": value.__class__.__module__,
                    "data": value.model_dump(),
                }
            ).encode("utf-8")

        elif isinstance(value, dict):
            return json.dumps(value).encode("utf-8")

        return super().encode(value)

    def decode(self, value, force=False):
        """Extended decoding to restore datetime and Pydantic models."""
        if self.decode_responses or force:
            if isinstance(value, bytes):
                value = value.decode(self.encoding, self.encoding_errors)
                try:
                    data = json.loads(value)
                    if isinstance(data, dict) and "__type__" in data:
                        if data["__type__"] == "datetime":
                            return datetime.fromisoformat(data["value"])

                        elif data["__type__"] == "pydantic":
                            module_name = data.get("module")
                            model_name = data.get("model")
                            payload = data.get("data")

                            # Dynamically import model class
                            module = __import__(module_name, fromlist=[model_name])
                            model_cls: type[BaseModel] = getattr(module, model_name)
                            return model_cls(**payload)

                    return data
                except json.JSONDecodeError:
                    raise
        return value


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
                        encoder_class=CustomJsonEncoder,
                        encoding="utf-8",
                        encoding_errors="strict",
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
