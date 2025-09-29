# SPDX-License-Identifier: MIT
"""Context variable for storing current user authentication context.

This module provides a thread-local and async-safe way to store and access
the current authenticated user's ID throughout the request lifecycle.
"""

from contextvars import ContextVar
from typing import Any, Optional

from loguru import logger

# Type aliases for better readability
UserID = Optional[int]

# Context variable declaration
_current_user_id: ContextVar[UserID] = ContextVar("current_user_id", default=None)


def set_current_user(user_id: int) -> Any:
    """Set the current user ID in context.

    Args:
        user_id: The authenticated user's ID (must be positive integer)

    Returns:
        Token that can be used to reset the context

    Raises:
        ValueError: If user_id is not a positive integer
    """
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("user_id must be a positive integer")

    logger.debug("Setting current user context: user_id=%s", user_id)
    return _current_user_id.set(user_id)


def get_current_user() -> UserID:
    """Get the current user ID from context.

    Returns:
        The current user ID or None if not set
    """
    user_id = _current_user_id.get()
    if user_id is None:
        logger.warning("Attempted to get current user ID but context is not set")
    return user_id


def clear_current_user(token: Any) -> None:
    """Reset the current user context.

    Args:
        token: The token returned by set_current_user
    """
    _current_user_id.reset(token)
    logger.debug("Cleared current user context")
