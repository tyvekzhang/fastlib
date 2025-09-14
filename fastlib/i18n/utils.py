# SPDX-License-Identifier: MIT
"""
Internationalization utilities
"""

from typing import Optional

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


def _resolve_language(language: Optional[Language]) -> Language:
    """Return given language or current context default"""
    return language or I18nContext.get_language()


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
