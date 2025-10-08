# SPDX-License-Identifier: MIT
"""
Enums for stream module
"""

from enum import Enum


class MessageRole(str, Enum):
    """Message role enumeration"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class MessageStatus(str, Enum):
    """Message status enumeration"""

    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StreamEventType(str, Enum):
    """Stream event type"""

    START = "start"
    CONTENT = "content"
    FUNCTION_CALL = "function_call"
    ERROR = "error"
    END = "end"
    METADATA = "metadata"
