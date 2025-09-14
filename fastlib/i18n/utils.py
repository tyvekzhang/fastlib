"""
Internationalization utilities
"""

from typing import Any, Optional

from .manager import I18nContext
from .messages import get_message
from .types import Language

# Default language
DEFAULT_LANGUAGE = Language.ENGLISH

# Language alias mapping
LANGUAGE_MAPPING = {
    "zh": Language.CHINESE,
    "zh_cn": Language.CHINESE,
    "en": Language.ENGLISH,
    "en_us": Language.ENGLISH,
}

# --- Helpers ---


def _resolve_language(language: Optional[Language]) -> Language:
    """Return given language or current context default"""
    return language or I18nContext.get_language()


# --- Core utilities ---


def parse_language(language_str: Optional[str]) -> Language:
    """Parse string like 'zh-CN', 'en-US' to Language enum"""
    if not language_str:
        return DEFAULT_LANGUAGE
    return LANGUAGE_MAPPING.get(
        language_str.lower().replace("-", "_"), DEFAULT_LANGUAGE
    )


def get_localized_message(
    category: str, key: str, language: Optional[Language] = None
) -> str:
    """Get localized message by category ('error', 'success', 'business')"""
    lang = _resolve_language(language)
    return get_message(category, key, lang)


def get_error_message(key: str, language: Optional[Language] = None) -> str:
    return get_localized_message("error", key, language)


def get_success_message(key: str, language: Optional[Language] = None) -> str:
    return get_localized_message("success", key, language)


def create_error_response(
    error_key: str,
    language: Optional[Language] = None,
    details: Optional[str] = None,
    error_code: int = 400,
) -> dict[str, Any]:
    lang = _resolve_language(language)
    error = {
        "code": error_code,
        "message": get_error_message(error_key, lang),
        "language": lang.value,
    }
    if details:
        error["details"] = details
    return {"success": False, "error": error}


def create_success_response(
    data: Any,
    language: Optional[Language] = None,
    message_key: str = "search_success",
) -> dict[str, Any]:
    lang = _resolve_language(language)
    return {
        "success": True,
        "data": data,
        "message": get_success_message(message_key, lang),
        "language": lang.value,
    }
