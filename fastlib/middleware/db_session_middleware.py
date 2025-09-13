# SPDX-License-Identifier: MIT
"""Session proxy used in the project"""

from contextvars import ContextVar
from typing import Optional, Union

from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.types import ASGIApp

try:
    from sqlalchemy.ext.asyncio import async_sessionmaker
except ImportError:
    from sqlalchemy.orm import sessionmaker as async_sessionmaker


def create_middleware_and_session_proxy():
    """Create and return SQLAlchemy middleware and session proxy classes."""
    _Session: Optional[async_sessionmaker] = None
    _session: ContextVar[Optional[AsyncSession]] = ContextVar("_session", default=None)

    class SQLAlchemyMiddleware(BaseHTTPMiddleware):
        """Middleware for managing SQLAlchemy sessions in FastAPI applications."""

        def __init__(
            self,
            app: ASGIApp,
            db_url: Optional[Union[str, URL]] = None,
            custom_engine: Optional[Engine] = None,
            engine_args: dict = None,
            session_args: dict = None,
            commit_on_exit: bool = True,
        ):
            """Initialize the middleware with database configuration."""
            super().__init__(app)
            self.commit_on_exit = commit_on_exit
            engine_args = engine_args or {}
            session_args = session_args or {}

            if not custom_engine and not db_url:
                raise ValueError(
                    "You need to pass a db_url or a custom_engine parameter."
                )
            if not custom_engine:
                engine = create_async_engine(db_url, **engine_args)
            else:
                engine = custom_engine

            nonlocal _Session
            _Session = async_sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False,
                **session_args,
            )

        async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
            """Manage database session for each request."""
            async with DBSession(commit_on_exit=self.commit_on_exit):
                return await call_next(request)

    class DBSessionMeta(type):
        """Metaclass for DBSession providing session property."""

        @property
        def session(self) -> AsyncSession:
            """Get the current async context session."""
            if _Session is None:
                raise ValueError("Session is not initialised")

            session = _session.get()
            if session is None:
                raise ValueError("Session is not initialised")

            return session

    class DBSession(metaclass=DBSessionMeta):
        """Context manager for database sessions."""

        def __init__(self, session_args: dict = None, commit_on_exit: bool = False):
            """Initialize session context manager."""
            self.token = None
            self.session_args = session_args or {}
            self.commit_on_exit = commit_on_exit

        async def __aenter__(self):
            """Enter session context."""
            if _Session is None:
                raise ValueError("Session is not initialised")

            self.token = _session.set(_Session(**self.session_args))  # type: ignore
            return type(self)

        async def __aexit__(self, exc_type, exc_value, traceback):
            """Exit session context, handling commit/rollback."""
            session = _session.get()

            try:
                if exc_type is not None:
                    await session.rollback()
                elif self.commit_on_exit:
                    await session.commit()
            finally:
                await session.close()
                _session.reset(self.token)

    return SQLAlchemyMiddleware, DBSession


SQLAlchemyMiddleware, db = create_middleware_and_session_proxy()
