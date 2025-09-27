# SPDX-License-Identifier: MIT
"""
Internationalization context manager
"""

import contextvars
import functools
from collections.abc import Awaitable
from typing import Any, Callable, TypeVar

from fastlib.i18n.types import Language

_language_context = contextvars.ContextVar("language", default=Language.ENGLISH)

F = TypeVar("F", bound=Callable[..., Any])


def set_language(language: Language) -> None:
    """Set current language"""
    _language_context.set(language)


def get_language() -> Language:
    """Get current language"""
    return _language_context.get()


def get_language_code() -> str:
    """Get current language code, e.g. 'en', 'zh'"""
    return get_language().value


def reset_language() -> None:
    """Reset language to default"""
    _language_context.set(Language.ENGLISH)


def is_language(language: Language) -> bool:
    """Check if current language matches"""
    return get_language() == language


class I18nContext:
    """Context manager to temporarily switch language"""

    def __init__(self, language: Language):
        self.language = language
        self._token: contextvars.Token | None = None

    def __enter__(self):
        self._token = _language_context.set(self.language)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._token is not None:
            _language_context.reset(self._token)


def _language_context_decorator(
    language: Language, is_async: bool = False
) -> Callable[[F], F]:
    """Internal generator for sync/async language context decorators"""

    def decorator(func: F) -> F:
        if is_async:

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                with I18nContext(language):
                    return await func(*args, **kwargs)

            return async_wrapper
        else:

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                with I18nContext(language):
                    return func(*args, **kwargs)

            return wrapper

    return decorator


def language_context(language: Language) -> Callable[[F], F]:
    """Decorator: run a sync function within a language context"""
    return _language_context_decorator(language, is_async=False)


def async_language_context(
    language: Language,
) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """Decorator: run an async function within a language context"""
    return _language_context_decorator(language, is_async=True)


def i18n_context(language: Language) -> I18nContext:
    """Helper to create context manager"""
    return I18nContext(language)
