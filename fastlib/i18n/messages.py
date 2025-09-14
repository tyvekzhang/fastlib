# SPDX-License-Identifier: MIT
"""Load i18n data and export get message method"""

import json
from pathlib import Path
from typing import Optional, Union

from fastlib.constant import RESOURCE_DIR
from fastlib.i18n.types import Language

from .manager import get_language

DEFAULT_BASE_DIR = Path(RESOURCE_DIR) / "i18n"
TRANSLATIONS = {
    "zh": {"debug": {"test_message": "这是一条调试测试消息"}},
    "en": {"debug": {"test_message": "This is a debug test message"}},
}


def load_translations(base_dirs: Union[Path, list[Path], None] = None):
    """Load translation files from specified directories.

    Args:
        base_dirs: Path or list of paths to translation directories.

    File structure:
        base_dir/{lang}/{namespace}.json
        Example: i18n/en/error.json

    Note: Later directories override earlier ones for duplicate keys.
    """
    if base_dirs is None:
        base_dirs = [DEFAULT_BASE_DIR]
    elif isinstance(base_dirs, Path):
        base_dirs = [base_dirs]

    for base_dir in base_dirs:
        if not base_dir.exists():
            continue  # Skip if directory doesn't exist

        for lang in [Language.CHINESE, Language.ENGLISH]:
            lang_dir = base_dir / lang.value
            if not lang_dir.exists():
                continue  # Skip if language directory doesn't exist

            # Initialize language dict if not exists
            if lang.value not in TRANSLATIONS:
                TRANSLATIONS[lang.value] = {}

            for file in lang_dir.glob("*.json"):
                namespace = (
                    file.stem
                )  # Determine message_type from filename, e.g., error, success
                with open(file, encoding="utf-8") as f:
                    translations_data = json.load(f)

                    # Merge with existing namespace data or create new
                    if namespace in TRANSLATIONS[lang.value]:
                        TRANSLATIONS[lang.value][namespace].update(translations_data)
                    else:
                        TRANSLATIONS[lang.value][namespace] = translations_data


def get_message(
    message_type: str, key: str, language: Optional[Language] = None
) -> str:
    """Get translated message for given type, key and language.

    Args:
        message_type: Namespace/category of the message (e.g., 'error', 'success')
        key: Message identifier key
        language: Target language

    Returns:
        Translated message or fallback to default language if not found
    """

    if not language:
        language = get_language()
    # Try to get message from requested language
    lang_dict = TRANSLATIONS.get(language.value, {})
    msg = lang_dict.get(message_type, {}).get(key)
    print(f"lang_dict: {lang_dict}")
    if msg:
        return msg

    default_language = Language.ENGLISH.value
    # Fallback to default language
    return (
        TRANSLATIONS.get(default_language, {})
        .get(message_type, {})
        .get(key, f"Unknown {message_type} message: {key}")
    )
