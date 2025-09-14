# SPDX-License-Identifier: MIT
"""
Internationalization type definitions with extensible language support
"""

from enum import Enum
from typing import Optional


class Language(Enum):
    """Extensible language enumeration with metadata support"""

    CHINESE = "zh"
    ENGLISH = "en"

    # Language metadata (can be extended)
    _metadata: dict[str, dict[str, str]] = {
        "zh": {"name": "Chinese", "native_name": "中文", "direction": "ltr"},
        "en": {"name": "English", "native_name": "English", "direction": "ltr"},
    }

    @property
    def display_name(self) -> str:
        """Get language display name"""
        return self._metadata[self.value]["name"]

    @property
    def native_name(self) -> str:
        """Get native language name"""
        return self._metadata[self.value]["native_name"]

    @property
    def direction(self) -> str:
        """Get text direction (ltr/rtl)"""
        return self._metadata[self.value]["direction"]

    @classmethod
    def register(
        cls, code: str, name: str, native_name: str, direction: str = "ltr"
    ) -> None:
        """Register a new language dynamically

        Args:
            code: Language code (e.g., 'es', 'fr')
            name: English display name
            native_name: Native language name
            direction: Text direction ('ltr' or 'rtl')
        """
        if hasattr(cls, code.upper()):
            raise ValueError(f"Language {code} already registered")

        # Create new enum member
        new_member = Enum.value.__new__(cls)
        new_member._value_ = code
        cls._member_map_[code.upper()] = new_member
        cls._member_names_.append(code.upper())

        # Add metadata
        cls._metadata[code] = {
            "name": name,
            "native_name": native_name,
            "direction": direction,
        }

    @classmethod
    def from_code(cls, code: str) -> Optional["Language"]:
        """Get Language enum from language code

        Args:
            code: Language code (e.g., 'zh', 'en')

        Returns:
            Language enum or None if not found
        """
        code_upper = code.upper()
        return cls._member_map_.get(code_upper)

    @classmethod
    def supported_codes(cls) -> set[str]:
        """Get set of all supported language codes"""
        return {member.value for member in cls}

    @classmethod
    def is_supported(cls, code: str) -> bool:
        """Check if language code is supported"""
        return code in cls.supported_codes()


# if __name__ == "__main__":
#     # Register new languages dynamically
#     Language.register("es", "Spanish", "Español")
#     Language.register("ja", "Japanese", "日本語")
#     Language.register("ar", "Arabic", "العربية", "rtl")

#     # Access new languages
#     spanish = Language.ES
#     print(f"Spanish code: {spanish.value}")  # es
#     print(f"Spanish native: {spanish.native_name}")  # Español

#     # Check support
#     print(Language.is_supported("fr"))  # False
#     print(Language.is_supported("ja"))  # True

#     # Get from code
#     japanese = Language.from_code("ja")
#     print(japanese.display_name)  # Japanese
