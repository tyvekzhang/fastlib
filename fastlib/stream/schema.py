# SPDX-License-Identifier: MIT
"""
Schema for stream module
"""

from __future__ import annotations

import uuid
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, Field

from fastlib.stream.enums import MessageStatus

# Type alias for notification types for better readability and reusability
NotifyType = Literal[
    "message_updated",
    "message_cancelled",
    "message_failed",
    "message_completed",
]


class BaseStreamMessage(BaseModel):
    """Base model for a stream message chunk."""

    event: str
    data: Any | None = None


class NotifyStreamMessageData(BaseModel):
    """Data model for a notification message."""

    type: NotifyType
    message: str


class NotifyStreamMessage(BaseStreamMessage):
    """Represents a notification message within the stream."""

    event: Literal["notify"] = "notify"
    data: NotifyStreamMessageData


# A central dictionary to hold notification messages.
# This prevents code duplication and makes it easy to add or change messages.
_NOTIFY_MESSAGES: dict[NotifyType, str] = {
    "message_updated": "The message has been updated.",
    "message_cancelled": "The message has been cancelled.",
    "message_failed": "The message has failed.",
    "message_completed": "The message has been completed.",
}


def create_notify_message(notify_type: NotifyType) -> NotifyStreamMessage:
    """
    Factory function to create a notification message of a specific type.

    Args:
        notify_type: The type of notification to create.

    Returns:
        An instance of NotifyStreamMessage.

    Raises:
        ValueError: If an unknown notification type is provided.
    """
    if notify_type not in _NOTIFY_MESSAGES:
        raise ValueError(f"Unknown notification type: {notify_type}")

    return NotifyStreamMessage(
        data=NotifyStreamMessageData(
            type=notify_type,
            message=_NOTIFY_MESSAGES[notify_type],
        )
    )


class MessageCancelledNotify(NotifyStreamMessage):
    """Message cancelled notify"""

    data: NotifyStreamMessageData = NotifyStreamMessageData(
        type="message_cancelled", message="message had been cancelled"
    )


class MessageFailedNotify(NotifyStreamMessage):
    """Message failed notify"""

    data: NotifyStreamMessageData = NotifyStreamMessageData(
        type="message_failed", message="message had been failed"
    )


class MessageCompletedNotify(NotifyStreamMessage):
    """Message completed notify"""

    data: NotifyStreamMessageData = NotifyStreamMessageData(
        type="message_completed", message="message had been completed"
    )


class MessageUpdatedNotify(NotifyStreamMessage):
    """Message updated notify"""

    data: NotifyStreamMessageData = NotifyStreamMessageData(
        type="message_updated", message="message had been updated"
    )


V = TypeVar("V", bound=BaseStreamMessage)


class BaseMessage(BaseModel, Generic[V]):
    """
    Base model for a complete message, which can contain multiple stream chunks.
    It uses a generic TypeVar 'V' to be flexible with the content type.
    """

    # Using standard string UUIDs for better compatibility and fewer dependencies.
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    status: MessageStatus = Field(
        default=MessageStatus.CREATED, description="The current status of the message."
    )
    content: list[V] = Field(
        default_factory=list, description="A list of message chunks."
    )

    # 2. Use timezone-aware datetime objects.
    # datetime.now(timezone.utc) is the modern replacement for datetime.utcnow().
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    async def update_status(self, status: MessageStatus) -> None:
        """Updates the message status and the updated_at timestamp."""
        self.status = status
        self.updated_at = datetime.now(UTC)

    async def append_chunks(self, chunks: Iterable[V]) -> None:
        """Appends new message chunks to the content and updates the timestamp."""
        self.content.extend(chunks)
        self.updated_at = datetime.now(UTC)
