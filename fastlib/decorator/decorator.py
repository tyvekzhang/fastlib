# SPDX-License-Identifier: MIT
"""Decorator module for making decorators."""

import functools
from typing import Any, Callable, Type

from fastlib.config.config_registry import BaseConfig, ConfigRegistry
from fastlib.i18n.i18n_context import I18nContextManager
from fastlib.i18n.i18n_types import Language


# Decorator for easy registration
def config_class(name: str):
    """
    Decorator to register a configuration class.

    Args:
        name: The name to register the configuration under

    Usage:
        @config_class("my_config")
        class MyConfig(BaseConfig):
            pass
    """

    def decorator(cls: Type[BaseConfig]):
        ConfigRegistry.register(name, cls)
        return cls

    return decorator


# Decorator for automatic language context
def language_context(language: Language) -> Callable:
    """
    Decorator to automatically set language context for a function

    Args:
        language: Language to set during function execution

    Returns:
        Decorator function

    Example:
        ```python
        @language_context(Language.ENGLISH)
        def greet_user(name):
            return translate("Hello, {name}!", name=name)

        # When called, function will use English translations
        result = greet_user("Alice")  # Returns "Hello, Alice!"
        ```

        ```python
        @language_context(Language.FRENCH)
        def get_french_menu():
            return translate("Today's special: {special}", special="Coq au Vin")

        # Function will use French translations
        menu = get_french_menu()  # Returns "Plat du jour: Coq au Vin"
        ```
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with I18nContextManager(language):
                return func(*args, **kwargs)

        return wrapper

    return decorator


# Async support
def async_language_context(language: Language) -> Callable:
    """
    Decorator for async functions with language context

    Args:
        language: Language to set during async function execution

    Returns:
        Async decorator function

    Example:
        ```python
        @async_language_context(Language.SPANISH)
        async def fetch_spanish_content():
            content = await get_content_from_api()
            return translate("Content: {text}", text=content)

        # When awaited, function will use Spanish translations
        result = await fetch_spanish_content()
        ```

        ```python
        @async_language_context(Language.GERMAN)
        async def process_german_data():
            data = await fetch_data()
            return {
                'title': translate("Data Report"),
                'content': translate("Processed {count} items", count=len(data))
            }

        # Function will use German translations when executed
        report = await process_german_data()
        ```
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            with I18nContextManager(language):
                return await func(*args, **kwargs)

        return async_wrapper

    return decorator
