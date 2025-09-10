# SPDX-License-Identifier: MIT
"""Database configuration for the application."""

import os
from typing import Optional

from fastlib.config.config import BaseConfig
from fastlib.config import project_config_util
from fastlib.config.project_config_util import get_sqlite_db_path


class DatabaseConfig(BaseConfig):
    def __init__(
        self,
        pool_size: int,
        max_overflow: int,
        pool_recycle: int,
        echo_sql: bool,
        pool_pre_ping: bool,
        enable_redis: bool,
        cache_host: str,
        cache_port: int,
        cache_pass: str,
        db_num: int,
        dialect: Optional[str] = None,
        url: Optional[str] = None,
    ) -> None:
        """
        Initializes database configuration.

        Args:
            dialect: The model of database.
            url: The url of database.
            pool_size: The pool size of database.
            max_overflow: The max overflow of database.
            pool_recycle: The pool recycle of database.
            echo_sql: Whether to echo sql statements.
            pool_pre_ping: Whether to pre ping.
            enable_redis: Whether to enable Redis cache.
            cache_host: Redis host address.
            cache_port: Redis port number.
            cache_pass: Redis password.
            db_num: Redis database number.
        """
        if dialect is None or len(dialect.strip()) == 0:
            dialect = project_config_util.get_db_dialect()
        self.dialect = dialect
        
        # Prioritize environment variable for database URL
        env_db_url = os.getenv('DATABASE_URL')
        if env_db_url:
            self.url = env_db_url
        elif url is None or len(url.strip()) == 0:
            if dialect == "sqlite" or dialect is None:
                url = get_sqlite_db_path()
            else:
                url = project_config_util.get_db_url()
            self.url = url
        else:
            self.url = url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_recycle = pool_recycle
        self.echo_sql = echo_sql
        self.pool_pre_ping = pool_pre_ping
        self.enable_redis = enable_redis
        self.cache_host = cache_host
        self.cache_port = cache_port
        
        # Prioritize environment variable for Redis password
        env_redis_pass = os.getenv('REDIS_PASSWORD')
        self.cache_pass = env_redis_pass if env_redis_pass is not None else cache_pass
        
        self.db_num = db_num

    def __str__(self) -> str:
        """
        Returns a string representation of the database configuration.

        Returns:
            A string representation of the DatabaseConfig instance.
        """
        return f"{self.__class__.__name__}({self.__dict__})"
