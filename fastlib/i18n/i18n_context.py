"""
Internationalization Context Manager
"""

import contextvars
import functools
from typing import Callable, Optional, Any

from fastlib.i18n.i18n_types import Language



# Create context variable
_language_context = contextvars.ContextVar("language", default=Language.ENGLISH)


class I18nContext:
    """Internationalization context manager"""
    
    @staticmethod
    def set_language(language: Language) -> None:
        """
        Set the current context language
        
        Args:
            language: Language enum value
        """
        _language_context.set(language)
    
    @staticmethod
    def get_language() -> Language:
        """
        Get the current context language
        
        Returns:
            Current language enum value
        """
        return _language_context.get()
    
    @staticmethod
    def reset_language() -> None:
        """Reset language to default value"""
        _language_context.set(Language.ENGLISH)
    
    @staticmethod
    def get_language_code() -> str:
        """
        Get the current language code string
        
        Returns:
            Language code string (e.g., "en", "zh")
        """
        return _language_context.get().value
    
    @staticmethod
    def is_language(language: Language) -> bool:
        """
        Check if current language matches the given language
        
        Args:
            language: Language to check against
            
        Returns:
            True if current language matches
        """
        return _language_context.get() == language


class I18nContextManager:
    """Internationalization context manager supporting with statements"""
    
    def __init__(self, language: Language):
        """
        Initialize context manager
        
        Args:
            language: Language to set
        """
        self.language = language
        self._previous_language: Optional[Language] = None
        self._token: Optional[contextvars.Token] = None
    
    def __enter__(self) -> "I18nContextManager":
        """Enter context - save current language and set new language"""
        self._previous_language = I18nContext.get_language()
        self._token = _language_context.set(self.language)
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context - restore previous language"""
        if self._token is not None:
            _language_context.reset(self._token)
        elif self._previous_language is not None:
            I18nContext.set_language(self._previous_language)


# Convenience functions
def set_language(language: Language) -> None:
    """Set current language"""
    I18nContext.set_language(language)


def get_language() -> Language:
    """Get current language"""
    return I18nContext.get_language()


def get_language_code() -> str:
    """Get current language code"""
    return I18nContext.get_language_code()


def reset_language() -> None:
    """Reset language to default"""
    I18nContext.reset_language()


def with_language(language: Language) -> I18nContextManager:
    """
    Create language context manager
    
    Args:
        language: Language to set
        
    Returns:
        Context manager instance
    """
    return I18nContextManager(language)


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
