"""
Internationalization Context Manager
"""

import contextvars
from typing import Optional, Any

from src.main.app.libs.i18n.i18n_types import Language



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