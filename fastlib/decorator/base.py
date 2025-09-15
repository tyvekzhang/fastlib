# SPDX-License-Identifier: MIT
"""Commonly used decorator modules"""
import asyncio
from functools import wraps
import functools
import hashlib
import json
import time
from typing import Any, Callable, Optional
from loguru import Logger

from fastlib.cache.manager import get_cache_client


def log_request_time(logger_name: Optional[str] = None):
    """
    Decorator to log API request execution time.

    Args:
        logger_name: Name of the logger instance to use. If None, uses default logger.

    Returns:
        Decorator function
    """

    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await _time_request_async(func, logger_name, *args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return _time_request_sync(func, logger_name, *args, **kwargs)

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


async def _time_request_async(func: Callable, logger_name: str, *args, **kwargs) -> Any:
    """
    Internal function to time and log async request execution.

    Args:
        func: The decorated function
        logger_name: Logger instance name
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Result of the function execution
    """
    # Get logger instance
    logger_instance = Logger.get_instance(logger_name)

    # Record start time
    start_time = time.time()

    try:
        # Execute the function
        result = await func(*args, **kwargs)

        # Calculate execution time
        execution_time = time.time() - start_time

        # Log success
        logger_instance.info(
            f"API endpoint {func.__name__} executed successfully",
            execution_time_ms=round(execution_time * 1000, 2),
            status="success",
            endpoint=func.__name__,
        )

        return result

    except Exception as e:
        # Calculate execution time (even if error occurred)
        execution_time = time.time() - start_time

        # Log error
        logger_instance.error(
            f"API endpoint {func.__name__} execution failed: {str(e)}",
            execution_time_ms=round(execution_time * 1000, 2),
            status="error",
            endpoint=func.__name__,
            exc_info=e,
        )

        # Re-raise the exception
        raise


def _time_request_sync(func: Callable, logger_name: str, *args, **kwargs) -> Any:
    """
    Internal function to time and log synchronous request execution.

    Args:
        func: The decorated function
        logger_name: Logger instance name
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Result of the function execution
    """
    # Get logger instance
    logger_instance = Logger.get_instance(logger_name)

    # Record start time
    start_time = time.time()

    try:
        # Execute the function
        result = func(*args, **kwargs)

        # Calculate execution time
        execution_time = time.time() - start_time

        # Log success
        logger_instance.info(
            f"API endpoint {func.__name__} executed successfully",
            execution_time_ms=round(execution_time * 1000, 2),
            status="success",
            endpoint=func.__name__,
        )

        return result

    except Exception as e:
        # Calculate execution time (even if error occurred)
        execution_time = time.time() - start_time

        # Log error
        logger_instance.error(
            f"API endpoint {func.__name__} execution failed: {str(e)}",
            execution_time_ms=round(execution_time * 1000, 2),
            status="error",
            endpoint=func.__name__,
            exc_info=e,
        )

        # Re-raise the exception
        raise


def prevent_duplicate_submission(
    key_prefix: str = "duplicate_submission",
    ttl: int = 60,
    include_args: bool = True,
    include_kwargs: bool = True,
    custom_key_func: Optional[Callable] = None,
):
    """Decorator to prevent duplicate submissions within a specified time window.

    Args:
        key_prefix: Prefix for the cache key
        ttl: Time to live in seconds for the duplicate check
        include_args: Whether to include function args in the cache key
        include_kwargs: Whether to include function kwargs in the cache key
        custom_key_func: Optional custom function to generate cache key

    Returns:
        Decorated function that prevents duplicate submissions
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if custom_key_func:
                cache_key = custom_key_func(*args, **kwargs)
            else:
                key_parts = [key_prefix, func.__name__]

                if include_args and args:
                    # Skip 'self' for instance methods
                    args_to_hash = (
                        args[1:] if args and hasattr(args[0], "__class__") else args
                    )
                    key_parts.append(str(args_to_hash))

                if include_kwargs and kwargs:
                    # Sort kwargs for consistent key generation
                    sorted_kwargs = json.dumps(kwargs, sort_keys=True)
                    key_parts.append(sorted_kwargs)

                # Create hash of the key parts for a shorter key
                key_content = ":".join(key_parts)
                cache_key = (
                    f"{key_prefix}:{hashlib.md5(key_content.encode()).hexdigest()}"
                )

            # Get cache client
            cache = await get_cache_client()

            # Check if request is duplicate
            existing = await cache.get(cache_key)
            if existing is not None:
                raise DuplicateSubmissionError(
                    f"Duplicate submission detected. Please wait {ttl} seconds before retrying."
                )

            # Set lock in cache
            await cache.set(cache_key, "locked", ttl=ttl)

            try:
                # Execute the original function
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                # On error, remove the lock to allow retry
                await cache.delete(cache_key)
                raise e

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            raise NotImplementedError(
                "Synchronous functions are not supported. "
                "Please use async functions with prevent_duplicate_submission decorator."
            )

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class DuplicateSubmissionError(Exception):
    """Exception raised when a duplicate submission is detected."""

    pass
