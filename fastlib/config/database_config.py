# SPDX-License-Identifier: MIT
"""Database configuration for the application."""

import os
from typing import Optional

import fastlib.config.utils as config_util
from fastlib.config.base import BaseConfig


class DatabaseConfig(BaseConfig):
    def __init__(
        self,
        dialect: Optional[str] = None,
        url: Optional[str] = None,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_recycle: int = 3600,
        pool_pre_ping: bool = True,
        echo_sql: bool = False,
        enable_redis: bool = False,
        cache_host: str = "localhost",
        cache_port: int = 6379,
        cache_pass: str = "",
        cache_db_num: int = 0,
    ) -> None:
        """
        Initializes database configuration.

        Args:
            dialect: The database dialect (e.g., mysql, postgresql, sqlite).
            url: The database connection URL. Overrides environment variable DATABASE_URL.
            pool_size: The number of connections to keep in the pool. Default: 10.
            max_overflow: The maximum number of connections beyond pool_size. Default: 20.
            pool_recycle: Connection recycle time in seconds. Default: 3600 (1 hour).
            pool_pre_ping: Whether to test connections for liveness. Default: True.
            echo_sql: Whether to log SQL statements. Default: False.
            enable_redis: Whether to enable Redis cache. Default: False.
            cache_host: Redis host address. Default: localhost.
            cache_port: Redis port number. Default: 6379.
            cache_pass: Redis password. Default: empty.
            cache_db_num: Redis database number. Default: 0.
        """
        # Database configuration
        if dialect is None or len(dialect.strip()) == 0:
            dialect = config_util.get_db_dialect()
        self.dialect = dialect

        # Prioritize environment variable for database URL
        env_db_url = os.getenv("DB_URL")
        if env_db_url:
            self.url = env_db_url
        elif url is None or len(url.strip()) == 0:
            if dialect == "sqlite" or dialect is None:
                url = config_util.get_sqlite_db_path()
            else:
                url = config_util.get_db_url()
            self.url = url
        else:
            self.url = url

        # Connection pool configuration
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_recycle = pool_recycle
        self.pool_pre_ping = pool_pre_ping
        self.echo_sql = echo_sql

        # Redis/cache configuration
        self.enable_redis = enable_redis
        self.cache_host = cache_host
        self.cache_port = cache_port

        # Prioritize environment variable for Redis password
        env_redis_pass = os.getenv("REDIS_PASSWORD")
        self.cache_pass = env_redis_pass if env_redis_pass is not None else cache_pass

        self.cache_db_num = cache_db_num

    def __str__(self) -> str:
        """
        Returns a string representation of the database configuration.

        Returns:
            A string representation of the DatabaseConfig instance.
        """
        return f"{self.__class__.__name__}({self.__dict__})"
