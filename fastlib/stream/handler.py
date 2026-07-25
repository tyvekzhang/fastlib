# SPDX-License-Identifier: MIT
"""
Handler for stream module
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections.abc import AsyncIterable
from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from fastlib.cache.manager import get_cache_client
from fastlib.logging.handlers import logger

from .schema import (
    BaseMessage,
    MessageCancelledNotify,
    MessageCompletedNotify,
    MessageFailedNotify,
    MessageStatus,
    MessageUpdatedNotify,
    V,
)

T = TypeVar("T", bound=BaseMessage[V])


class StreamHandler(ABC, Generic[T]):
    """Stream message handler"""

    def __init__(
        self,
        message: T,
        source: AsyncIterable[V],
        storage: Any,
    ):
        self._message = message
        self._source = source
        self._storage = storage or get_cache_client()

    @property
    def id(self) -> str:
        return self._message.id

    @property
    def message(self) -> T:
        return self._message

    @abstractmethod
    async def start(self) -> None:
        """Start processing"""
        pass

    @abstractmethod
    async def cancel(self) -> None:
        """Cancel processing"""
        pass

    @abstractmethod
    async def get_content_stream(self) -> AsyncIterable[V]:
        """Get content stream"""
        pass

    @abstractmethod
    async def update_message(self) -> None:
        """Update message"""
        pass


class AsyncStreamHandler(StreamHandler[T]):
    """Asynchronous (coroutine) stream message handler"""

    def __init__(
        self,
        message: T,
        source: AsyncIterable[V],
        storage: Any,
        buffer_size: int = 100,
    ):
        super().__init__(message, source, storage)

        self._buffer = list[V]()
        self._buffer_size = buffer_size
        self._content_queues = list[asyncio.Queue[V]]()
        self._task_ref: asyncio.Task | None = None

        # Store handler in cache
        if self._storage:
            asyncio.create_task(self._storage.set(self._message.id, self))

    async def start(self):
        """Start task processing"""
        assert self._task_ref is None

        self._task_ref = asyncio.create_task(self._run())

        await self._message.update_status(MessageStatus.RUNNING)

    async def cancel(self) -> None:
        """Cancel task processing"""
        if self._task_ref and not self._task_ref.done():
            self._task_ref.cancel()
            await self._task_ref

    async def _run(self):
        """Main processing loop"""
        try:
            async for item in self._source:
                # Push data to queues
                for queue in self._content_queues:
                    await queue.put(item)

                # Add data to buffer and update message when buffer is full
                self._buffer.append(item)
                if len(self._buffer) >= self._buffer_size:
                    await self.update_message()

        except asyncio.CancelledError:
            for queue in self._content_queues:
                queue.put_nowait(MessageCancelledNotify())
            await self.update_message()
            await self._message.update_status(MessageStatus.CANCELLED)

        except Exception as e:
            logger.exception(f"Stream source error: {e}")
            for queue in self._content_queues:
                queue.put_nowait(MessageFailedNotify())
            await self.update_message()
            await self._message.update_status(MessageStatus.FAILED)

        else:
            for queue in self._content_queues:
                queue.put_nowait(MessageCompletedNotify())
            await self.update_message()
            await self._message.update_status(MessageStatus.COMPLETED)

        finally:
            # Remove handler from cache
            if self._storage:
                await self._storage.delete(self._message.id)

    async def update_message(self) -> None:
        """Update message"""
        if not self._buffer:
            return

        ready_buffer = self._buffer
        self._buffer = list[V]()
        await self._message.append_chunks(ready_buffer)

    async def get_content_stream(
        self,
        message_updated_at: datetime | None = None,
        **model_dump_kwargs,
    ) -> AsyncIterable[str]:
        """Get content stream"""

        if message_updated_at and self._message.updated_at > message_updated_at:
            yield MessageUpdatedNotify().model_dump_json(**model_dump_kwargs)
            return

        _buffer_copy = list(self._buffer)
        queue = asyncio.Queue[V]()
        self._content_queues.append(queue)

        try:
            for item in _buffer_copy:
                yield item.model_dump_json(**model_dump_kwargs)

            while self._task_ref and not self._task_ref.done():
                item = await queue.get()
                if isinstance(item, dict):
                    import json

                    yield json.dumps(item)
                elif isinstance(item, BaseModel):
                    yield item.model_dump_json(**model_dump_kwargs)
                else:
                    yield item
                if isinstance(
                    item,
                    MessageCompletedNotify
                    | MessageCancelledNotify
                    | MessageFailedNotify,
                ):
                    break
        finally:
            self._content_queues.remove(queue)
