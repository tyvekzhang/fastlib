# SPDX-License-Identifier: MIT
"""Database configuration for the application."""

import os
from dataclasses import dataclass, field

import fastlib.config.utils as config_util
from fastlib.config.base import BaseConfig


@dataclass
class DatabaseConfig(BaseConfig):
    """
    Database configuration for the application.

    Attributes:
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
    dialect: str = field(default_factory=lambda: config_util.get_db_dialect() or "")
    url: str = field(default_factory=lambda: DatabaseConfig._get_default_db_url())
    pool_size: int = 10
    max_overflow: int = 20
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    echo_sql: bool = False

    # Redis/cache configuration
    enable_redis: bool = False
    cache_host: str = "localhost"
    cache_port: int = 6379
    cache_pass: str = field(default_factory=lambda: os.getenv("REDIS_PASSWORD", ""))
    cache_db_num: int = 0

    def __post_init__(self) -> None:
        """Post-initialization processing."""
        # Handle dialect default
        if not self.dialect.strip():
            self.dialect = config_util.get_db_dialect()

        # Handle URL priority: environment variable > parameter > default
        env_db_url = os.getenv("DB_URL")
        if env_db_url:
            self.url = env_db_url
        elif not self.url.strip():
            self.url = self._get_default_db_url()

        # Handle Redis password from environment
        env_redis_pass = os.getenv("REDIS_PASSWORD")
        if env_redis_pass is not None:
            self.cache_pass = env_redis_pass

    @staticmethod
    def _get_default_db_url() -> str:
        """Get default database URL based on dialect."""
        dialect = config_util.get_db_dialect()
        if dialect == "sqlite" or dialect is None:
            return config_util.get_sqlite_db_path()
        else:
            return config_util.get_db_url()
