# SPDX-License-Identifier: MIT
"""Thread-safe async SQLAlchemy engine management."""

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from fastlib import ConfigManager

async_engine: AsyncEngine


def get_async_engine() -> AsyncEngine:
    """
    Get or create a cached async SQLAlchemy engine with thread-safe initialization.

    Returns:
        AsyncEngine: Configured SQLAlchemy async engine based on application config.
    """
    global async_engine
    database_config = ConfigManager.get_database_config()
    if database_config.dialect.lower() == "sqlite":
        async_engine = create_async_engine(
            url=database_config.url,
            echo=database_config.echo_sql,
            pool_recycle=database_config.pool_recycle,
            pool_pre_ping=True,
        )
    else:
        async_engine = create_async_engine(
            url=database_config.url,
            echo=database_config.echo_sql,
            pool_size=database_config.pool_size,
            max_overflow=database_config.max_overflow,
            pool_recycle=database_config.pool_recycle,
            pool_pre_ping=True,
        )
    return async_engine
