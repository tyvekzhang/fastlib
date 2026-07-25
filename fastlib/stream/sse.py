# SPDX-License-Identifier: MIT
"""
Copy from https://github.com/sysid/sse-starlette/blob/main/sse_starlette/sse.py
"""

import contextvars
from collections.abc import (
    AsyncIterable,
    Awaitable,
    Callable,
    Coroutine,
    Iterator,
    Mapping,
)
from datetime import UTC, datetime
from typing import (
    Any,
)

import anyio
from starlette.background import BackgroundTask
from starlette.concurrency import iterate_in_threadpool
from starlette.datastructures import MutableHeaders
from starlette.responses import Response
from starlette.types import Message, Receive, Scope, Send

from fastlib.logging.handlers import logger
from fastlib.stream.event import ServerSentEvent, ensure_bytes

# Context variable for exit events per event loop
_exit_event_context: contextvars.ContextVar[anyio.Event | None] = (
    contextvars.ContextVar("exit_event", default=None)
)


class SendTimeoutError(TimeoutError):
    pass


class AppStatus:
    """Helper to capture a shutdown signal from Uvicorn so we can gracefully terminate SSE streams."""

    should_exit = False
    original_handler: Callable | None = None

    @staticmethod
    def handle_exit(*args, **kwargs):
        # Mark that the app should exit, and signal all waiters in all contexts.
        AppStatus.should_exit = True

        # Signal the event in current context if it exists
        current_event = _exit_event_context.get(None)
        if current_event is not None:
            current_event.set()

        if AppStatus.original_handler is not None:
            AppStatus.original_handler(*args, **kwargs)

    @staticmethod
    def get_or_create_exit_event() -> anyio.Event:
        """Get or create an exit event for the current context."""
        event = _exit_event_context.get(None)
        if event is None:
            event = anyio.Event()
            _exit_event_context.set(event)
        return event


try:
    from uvicorn.main import Server

    AppStatus.original_handler = Server.handle_exit
    Server.handle_exit = AppStatus.handle_exit  # type: ignore
except ImportError:
    logger.debug(
        "Uvicorn not installed. Graceful shutdown on server termination disabled."
    )

Content = str | bytes | dict | ServerSentEvent | Any
SyncContentStream = Iterator[Content]
AsyncContentStream = AsyncIterable[Content]
ContentStream = AsyncContentStream | SyncContentStream


class EventSourceResponse(Response):
    """
    Streaming response that sends data conforming to the SSE (Server-Sent Events) specification.
    """

    DEFAULT_PING_INTERVAL = 15
    DEFAULT_SEPARATOR = "\r\n"

    def __init__(
        self,
        content: ContentStream,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str = "text/event-stream",
        background: BackgroundTask | None = None,
        ping: int | None = None,
        sep: str | None = None,
        ping_message_factory: Callable[[], ServerSentEvent] | None = None,
        data_sender_callable: Callable[[], Coroutine[None, None, None]] | None = None,
        send_timeout: float | None = None,
        client_close_handler_callable: (
            Callable[[Message], Awaitable[None]] | None
        ) = None,
    ) -> None:
        # Validate separator
        if sep not in (None, "\r\n", "\r", "\n"):
            raise ValueError(f"sep must be one of: \\r\\n, \\r, \\n, got: {sep}")
        self.sep = sep or self.DEFAULT_SEPARATOR

        # If content is sync, wrap it for async iteration
        if isinstance(content, AsyncIterable):
            self.body_iterator = content
        else:
            self.body_iterator = iterate_in_threadpool(content)

        self.status_code = status_code
        self.media_type = self.media_type if media_type is None else media_type
        self.background = background
        self.data_sender_callable = data_sender_callable
        self.send_timeout = send_timeout

        # Build SSE-specific headers.
        _headers = MutableHeaders()
        if headers is not None:  # pragma: no cover
            _headers.update(headers)

        # "The no-store response directive indicates that any caches of any kind (private or shared)
        # should not store this response."
        # -- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
        # allow cache control header to be set by user to support fan out proxies
        # https://www.fastly.com/blog/server-sent-events-fastly

        _headers.setdefault("Cache-Control", "no-store")
        # mandatory for servers-sent events headers
        _headers["Connection"] = "keep-alive"
        _headers["X-Accel-Buffering"] = "no"
        self.init_headers(_headers)

        self.ping_interval = self.DEFAULT_PING_INTERVAL if ping is None else ping
        self.ping_message_factory = ping_message_factory

        self.client_close_handler_callable = client_close_handler_callable

        self.active = True
        # https://github.com/sysid/sse-starlette/pull/55#issuecomment-1732374113
        self._send_lock = anyio.Lock()

    @property
    def ping_interval(self) -> int | float:
        return self._ping_interval

    @ping_interval.setter
    def ping_interval(self, value: int | float) -> None:
        if not isinstance(value, int | float):
            raise TypeError("ping interval must be int")
        if value < 0:
            raise ValueError("ping interval must be greater than 0")
        self._ping_interval = value

    def enable_compression(self, force: bool = False) -> None:
        raise NotImplementedError("Compression is not supported for SSE streams.")

    async def _stream_response(self, send: Send) -> None:
        """Send out SSE data to the client as it becomes available in the iterator."""
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )

        async for data in self.body_iterator:
            chunk = ensure_bytes(data, self.sep)
            with anyio.move_on_after(self.send_timeout) as cancel_scope:
                await send(
                    {"type": "http.response.body", "body": chunk, "more_body": True}
                )

            if cancel_scope and cancel_scope.cancel_called:
                if hasattr(self.body_iterator, "aclose"):
                    await self.body_iterator.aclose()
                raise SendTimeoutError()

        async with self._send_lock:
            self.active = False
            await send({"type": "http.response.body", "body": b"", "more_body": False})

    async def _listen_for_disconnect(self, receive: Receive) -> None:
        """Watch for a disconnect message from the client."""
        while self.active:
            message = await receive()
            if message["type"] == "http.disconnect":
                self.active = False
                logger.debug("Got event: http.disconnect. Stop streaming.")
                if self.client_close_handler_callable:
                    await self.client_close_handler_callable(message)
                break

    @staticmethod
    async def _listen_for_exit_signal() -> None:
        """Watch for shutdown signals (e.g. SIGINT, SIGTERM) so we can break the event loop."""
        # Check if should_exit was set before anybody started waiting
        if AppStatus.should_exit:
            return

        # Get or create context-local exit event
        exit_event = AppStatus.get_or_create_exit_event()

        # Check if should_exit got set while we set up the event
        if AppStatus.should_exit:
            return

        await exit_event.wait()

    async def _ping(self, send: Send) -> None:
        """Periodically send ping messages to keep the connection alive on proxies.
        - frequenccy ca every 15 seconds.
        - Alternatively one can send periodically a comment line (one starting with a ':' character)
        """
        while self.active:
            await anyio.sleep(self._ping_interval)
            sse_ping = (
                self.ping_message_factory()
                if self.ping_message_factory
                else ServerSentEvent(
                    comment=f"ping - {datetime.now(UTC)}", sep=self.sep
                )
            )
            ping_bytes = ensure_bytes(sse_ping, self.sep)

            async with self._send_lock:
                if self.active:
                    await send(
                        {
                            "type": "http.response.body",
                            "body": ping_bytes,
                            "more_body": True,
                        }
                    )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Entrypoint for Starlette's ASGI contract. We spin up tasks:
        - _stream_response to push events
        - _ping to keep the connection alive
        - _listen_for_exit_signal to respond to server shutdown
        - _listen_for_disconnect to respond to client disconnect
        """
        async with anyio.create_task_group() as task_group:
            # https://trio.readthedocs.io/en/latest/reference-core.html#custom-supervisors
            async def cancel_on_finish(coro: Callable[[], Awaitable[None]]):
                await coro()
                task_group.cancel_scope.cancel()

            task_group.start_soon(cancel_on_finish, lambda: self._stream_response(send))
            task_group.start_soon(cancel_on_finish, lambda: self._ping(send))
            task_group.start_soon(cancel_on_finish, self._listen_for_exit_signal)

            if self.data_sender_callable:
                task_group.start_soon(self.data_sender_callable)

            # Wait for the client to disconnect last
            task_group.start_soon(
                cancel_on_finish, lambda: self._listen_for_disconnect(receive)
            )

        if self.background is not None:
            await self.background()
