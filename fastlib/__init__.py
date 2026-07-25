# SPDX-License-Identifier: MIT
"""Fastlib Application Libraries Package."""

from .config import ConfigManager as ConfigManager
from .openapi import register_offline_openapi as register_offline_openapi

__all__ = [
    "ConfigManager",
    "register_offline_openapi",
]
