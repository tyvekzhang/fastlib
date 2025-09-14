# SPDX-License-Identifier: MIT
"""Common constant"""

import os
from typing import Any

from fastlib.utils import file_util

# Default constant values
_DEFAULT_CONSTANTS: dict[str, Any] = {
    "RESOURCE_DIR": os.path.abspath(
        os.path.join(file_util.find_project_root(), "src", "main", "resource")
    ),
    "ADMIN_ID": 9,
    "ROOT_PARENT_ID": 0,
    "MAX_PAGE_SIZE": 1000,
    "ENV": "env",
    "PARENT_ID": "parent_id",
    "CONFIG_FILE": "config_file",
    "CONFIG_FILE_NAME": "config.yml",
    "AUTHORIZATION": "Authorization",
}

# Current constant values (initially defaults)
_CURRENT_CONSTANTS = _DEFAULT_CONSTANTS.copy()

# Exported constants (maintain original interface)
RESOURCE_DIR: str = _CURRENT_CONSTANTS["RESOURCE_DIR"]
ADMIN_ID = _CURRENT_CONSTANTS["ADMIN_ID"]
ROOT_PARENT_ID = _CURRENT_CONSTANTS["ROOT_PARENT_ID"]
MAX_PAGE_SIZE = _CURRENT_CONSTANTS["MAX_PAGE_SIZE"]
ENV = _CURRENT_CONSTANTS["ENV"]
PARENT_ID = _CURRENT_CONSTANTS["PARENT_ID"]
CONFIG_FILE = _CURRENT_CONSTANTS["CONFIG_FILE"]
CONFIG_FILE_NAME = _CURRENT_CONSTANTS["CONFIG_FILE_NAME"]
AUTHORIZATION = _CURRENT_CONSTANTS["AUTHORIZATION"]


def set_constant(name: str, value: Any) -> None:
    """Set constant value.

    Args:
        name: Constant name
        value: New value

    Raises:
        ValueError: If constant doesn't exist
    """
    if name not in _DEFAULT_CONSTANTS:
        raise ValueError(f"Constant '{name}' doesn't exist")

    _CURRENT_CONSTANTS[name] = value
    _update_exported_constants()


def reset_constant(name: str = None) -> None:
    """Reset constant(s) to default values.

    Args:
        name: Constant name to reset, None resets all

    Raises:
        ValueError: If constant doesn't exist
    """
    if name is None:
        _CURRENT_CONSTANTS.clear()
        _CURRENT_CONSTANTS.update(_DEFAULT_CONSTANTS)
    else:
        if name not in _DEFAULT_CONSTANTS:
            raise ValueError(f"Constant '{name}' doesn't exist")
        _CURRENT_CONSTANTS[name] = _DEFAULT_CONSTANTS[name]

    _update_exported_constants()


def get_constant(name: str) -> Any:
    """Get current constant value.

    Args:
        name: Constant name

    Returns:
        Current constant value

    Raises:
        ValueError: If constant doesn't exist
    """
    if name not in _CURRENT_CONSTANTS:
        raise ValueError(f"Constant '{name}' doesn't exist")
    return _CURRENT_CONSTANTS[name]


def get_default_constant(name: str) -> Any:
    """Get default constant value.

    Args:
        name: Constant name

    Returns:
        Default constant value

    Raises:
        ValueError: If constant doesn't exist
    """
    if name not in _DEFAULT_CONSTANTS:
        raise ValueError(f"Constant '{name}' doesn't exist")
    return _DEFAULT_CONSTANTS[name]


def list_constants() -> dict[str, dict[str, Any]]:
    """List all constants with current and default values.

    Returns:
        Dictionary with constant information
    """
    return {
        name: {
            "current": _CURRENT_CONSTANTS[name],
            "default": _DEFAULT_CONSTANTS[name],
            "is_modified": _CURRENT_CONSTANTS[name] != _DEFAULT_CONSTANTS[name],
        }
        for name in _DEFAULT_CONSTANTS
    }


def _update_exported_constants() -> None:
    """Update exported constant variables."""
    global RESOURCE_DIR, ADMIN_ID, ROOT_PARENT_ID, MAX_PAGE_SIZE
    global ENV, PARENT_ID, CONFIG_FILE, CONFIG_FILE_NAME, AUTHORIZATION

    RESOURCE_DIR = _CURRENT_CONSTANTS["RESOURCE_DIR"]
    ADMIN_ID = _CURRENT_CONSTANTS["ADMIN_ID"]
    ROOT_PARENT_ID = _CURRENT_CONSTANTS["ROOT_PARENT_ID"]
    MAX_PAGE_SIZE = _CURRENT_CONSTANTS["MAX_PAGE_SIZE"]
    ENV = _CURRENT_CONSTANTS["ENV"]
    PARENT_ID = _CURRENT_CONSTANTS["PARENT_ID"]
    CONFIG_FILE = _CURRENT_CONSTANTS["CONFIG_FILE"]
    CONFIG_FILE_NAME = _CURRENT_CONSTANTS["CONFIG_FILE_NAME"]
    AUTHORIZATION = _CURRENT_CONSTANTS["AUTHORIZATION"]


class FilterOperators:
    EQ = "EQ"
    NE = "NE"
    GT = "GT"
    GE = "GE"
    LT = "LT"
    LE = "LE"
    BETWEEN = "BETWEEN"
    LIKE = "LIKE"
