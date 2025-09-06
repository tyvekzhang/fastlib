"""
Internationalization message configuration file
"""

from i18n_types import Language


# Error message internationalization
ERROR_MESSAGES = {
    Language.CHINESE: {
        "invalid_request": "无效的请求参数",
    },
    Language.ENGLISH: {
        "invalid_request": "Invalid request parameters",
    },
}


# Mapping of all message types
SUCCESS_MESSAGES = {
    Language.CHINESE: {
        "operation_success": "操作成功",
    },
    Language.ENGLISH: {
        "operation_success": "Operation successful",
    },
}

ALL_MESSAGE_TYPES = {
    "error": ERROR_MESSAGES,
    "success": SUCCESS_MESSAGES,
}


def get_message(message_type: str, key: str, language: Language) -> str:
    """
    Get internationalized message of specified type

    Args:
        message_type: Message type (error, success, status, label, system, business)
        key: Message key
        language: Language

    Returns:
        Internationalized message string
    """
    if message_type not in ALL_MESSAGE_TYPES:
        return f"Unknown message type: {message_type}"

    messages = ALL_MESSAGE_TYPES[message_type]
    default_language = Language.CHINESE

    return messages.get(language, messages[default_language]).get(
        key,
        messages[default_language].get(key, f"Unknown {message_type} message: {key}"),
    )


def get_all_messages_for_language(language: Language) -> dict:
    """
    Get all messages for specified language

    Args:
        language: Language

    Returns:
        Dictionary containing all message types
    """
    result = {}
    for message_type, messages in ALL_MESSAGE_TYPES.items():
        result[message_type] = messages.get(language, messages[Language.CHINESE])
    return result


def get_available_message_types() -> list:
    """
    Get all available message types

    Returns:
        List of message types
    """
    return list(ALL_MESSAGE_TYPES.keys())


def get_available_keys_for_type(message_type: str) -> list:
    """
    Get all available keys for specified message type

    Args:
        message_type: Message type

    Returns:
        List of keys
    """
    if message_type not in ALL_MESSAGE_TYPES:
        return []

    messages = ALL_MESSAGE_TYPES[message_type]
    # Use Chinese as default language to get all keys
    return list(messages[Language.CHINESE].keys())