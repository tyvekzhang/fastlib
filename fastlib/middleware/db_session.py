# SPDX-License-Identifier: MIT
"""Session proxy used in the project"""

from contextvars import ContextVar

from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.types import ASGIApp, Receive, Scope, Send

try:
    from sqlalchemy.ext.asyncio import async_sessionmaker
except ImportError:
    from sqlalchemy.orm import sessionmaker as async_sessionmaker


def create_middleware_and_session_proxy():
    """Create and return SQLAlchemy middleware and session proxy classes."""
    _Session: async_sessionmaker | None = None
    _session: ContextVar[AsyncSession | None] = ContextVar("_session", default=None)

    class SQLAlchemyMiddleware:
        """
        Pure ASGI middleware that keeps one AsyncSession alive for the full
        request — including StreamingResponse / SSE body iteration.

        BaseHTTPMiddleware closes the session as soon as response.start is
        sent, which races with generators still using db.session (SQLAlchemy
        isce: close() while _connection_for_bind() is in progress).
        """

        def __init__(
            self,
            app: ASGIApp,
            db_url: str | URL | None = None,
            custom_engine: Engine | None = None,
            engine_args: dict = None,
            session_args: dict = None,
            commit_on_exit: bool = True,
        ):
            """Initialize the middleware with database configuration."""
            self.app = app
            self.commit_on_exit = commit_on_exit
            engine_args = engine_args or {}
            session_args = session_args or {}

            if not custom_engine and not db_url:
                raise RuntimeError(
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

        async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
            if scope["type"] != "http":
                await self.app(scope, receive, send)
                return

            async with DBSession(commit_on_exit=self.commit_on_exit):
                await self.app(scope, receive, send)

    class DBSessionMeta(type):
        """Metaclass for DBSession providing session property."""

        @property
        def session(self) -> AsyncSession:
            """Get the current async context session."""
            if _Session is None:
                raise RuntimeError("Session is not initialised")

            session = _session.get()
            if session is None:
                raise RuntimeError("Session is not initialised")

            return session

    class DBSession(metaclass=DBSessionMeta):
        """Context manager for database sessions."""

        def __init__(self, session_args: dict = None, commit_on_exit: bool = False):
            """Initialize session context manager."""
            self.token = None
            self._owned_session: AsyncSession | None = None
            self.session_args = session_args or {}
            self.commit_on_exit = commit_on_exit

        async def __aenter__(self):
            """Enter session context."""
            if _Session is None:
                raise RuntimeError("Session is not initialised")

            self._owned_session = _Session(**self.session_args)  # type: ignore
            self.token = _session.set(self._owned_session)
            return type(self)

        async def __aexit__(self, exc_type, exc_value, traceback):
            """Exit session context, handling commit/rollback."""
            # Always close the session this context created — never the nested
            # current ContextVar value (which may belong to an inner async with db()).
            session = self._owned_session
            if session is None:
                if self.token is not None:
                    _session.reset(self.token)
                return

            try:
                if exc_type is not None:
                    await session.rollback()
                elif self.commit_on_exit:
                    await session.commit()
            finally:
                await session.close()
                if self.token is not None:
                    _session.reset(self.token)
                self._owned_session = None

    return SQLAlchemyMiddleware, DBSession


SQLAlchemyMiddleware, db = create_middleware_and_session_proxy()
