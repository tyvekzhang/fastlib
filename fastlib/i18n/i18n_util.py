"""
Internationalization utility class supporting Chinese and English language switching
"""

from typing import Dict, Any, Optional
from .i18n_types import Language
from .i18n_messages import get_message
from .i18n_context import I18nContext


class I18nUtil:
    """Internationalization utility class"""

    # Default language
    DEFAULT_LANGUAGE = Language.ENGLISH

    # Language mapping
    LANGUAGE_MAPPING = {
        "zh": Language.CHINESE,
        "zh_cn": Language.CHINESE,
        "en": Language.ENGLISH,
        "en_us": Language.ENGLISH,
    }

    @classmethod
    def parse_language(cls, language_str: Optional[str]) -> Language:
        """
        Parse language string
        
        Args:
            language_str: Language string (e.g., "zh", "en", "zh-CN", "en-US")
            
        Returns:
            Language enum value
            
        Example:
            >>> I18nUtil.parse_language("zh-CN")
            <Language.CHINESE: 'zh'>
            >>> I18nUtil.parse_language("invalid")
            <Language.ENGLISH: 'en'>
        """
        if not language_str:
            return cls.DEFAULT_LANGUAGE

        # Normalize language string
        normalized = language_str.lower()
        # Handle hyphens and underscores
        normalized = normalized.replace("-", "_")

        return cls.LANGUAGE_MAPPING.get(normalized, cls.DEFAULT_LANGUAGE)

    @classmethod
    def get_error_message(cls, key: str, language: Optional[Language] = None) -> str:
        """
        Get error message
        
        Args:
            key: Error message key
            language: Language, if None uses context language
            
        Returns:
            Error message string
            
        Example:
            >>> I18nUtil.get_error_message("invalid_input", Language.CHINESE)
            "无效输入"
        """
        if language is None:
            language = I18nContext.get_language()

        return get_message("error", key, language)

    @classmethod
    def get_success_message(cls, key: str, language: Optional[Language] = None) -> str:
        """
        Get success message
        
        Args:
            key: Success message key
            language: Language, if None uses context language
            
        Returns:
            Success message string
        """
        if language is None:
            language = I18nContext.get_language()

        return get_message("success", key, language)
        """
        Get business message
        
        Args:
            key: Business message key
            language: Language, if None uses context language
            
        Returns:
            Business message string
        """
        if language is None:
            language = I18nContext.get_language()

        return get_message("business", key, language)

    @classmethod
    def create_error_response(
        cls,
        error_key: str,
        language: Optional[Language] = None,
        details: Optional[str] = None,
        error_code: int = 400,
    ) -> Dict[str, Any]:
        """
        Create error response
        
        Args:
            error_key: Error message key
            language: Language
            details: Error details
            error_code: Error code
            
        Returns:
            Error response dictionary
            
        Example:
            >>> response = I18nUtil.create_error_response(
            ...     "invalid_input", 
            ...     Language.ENGLISH,
            ...     "Email format is incorrect",
            ...     422
            ... )
            >>> print(response)
            {
                "success": False,
                "error": {
                    "code": 422,
                    "message": "Invalid input",
                    "language": "en",
                    "details": "Email format is incorrect"
                }
            }
        """
        if language is None:
            language = I18nContext.get_language()

        response = {
            "success": False,
            "error": {
                "code": error_code,
                "message": cls.get_error_message(error_key, language),
                "language": language.value,
            },
        }

        if details:
            response["error"]["details"] = details

        return response

    @classmethod
    def create_success_response(
        cls,
        data: Any,
        language: Optional[Language] = None,
        message_key: str = "search_success",
    ) -> Dict[str, Any]:
        """
        Create success response
        
        Args:
            data: Response data
            language: Language
            message_key: Success message key
            
        Returns:
            Success response dictionary
            
        Example:
            >>> response = I18nUtil.create_success_response(
            ...     {"user": {"id": 1, "name": "John"}},
            ...     Language.CHINESE,
            ...     "operation_success"
            ... )
            >>> print(response)
            {
                "success": True,
                "data": {"user": {"id": 1, "name": "John"}},
                "message": "操作成功",
                "language": "zh"
            }
        """
        if language is None:
            language = I18nContext.get_language()

        return {
            "success": True,
            "data": data,
            "message": cls.get_success_message(message_key, language),
            "language": language.value,
        }

# Convenience functions
def get_language(language_str: Optional[str]) -> Language:
    """Get language enum value"""
    return I18nUtil.parse_language(language_str)


def get_error_message(key: str, language: Optional[Language] = None) -> str:
    """Get error message"""
    return I18nUtil.get_error_message(key, language)


def get_success_message(key: str, language: Optional[Language] = None) -> str:
    """Get success message"""
    return I18nUtil.get_success_message(key, language)


def create_error_response(
    error_key: str,
    language: Optional[Language] = None,
    details: Optional[str] = None,
    error_code: int = 400,
) -> Dict[str, Any]:
    """Create error response"""
    return I18nUtil.create_error_response(error_key, language, details, error_code)


def create_success_response(
    data: Any, language: Optional[Language] = None, message_key: str = "search_success"
) -> Dict[str, Any]:
    """Create success response"""
    return I18nUtil.create_success_response(data, language, message_key)