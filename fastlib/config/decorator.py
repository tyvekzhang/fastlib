# SPDX-License-Identifier: MIT
"""Decorator for easy registration"""

from fastlib.config.base import BaseConfig
from fastlib.config.registry import ConfigRegistry


def config_class(name: str):
    """
    Decorator to register a configuration class.

    Args:
        name: The name to register the configuration under

    Usage:
        @config_class("my_config")
        class MyConfig(BaseConfig):
            pass
    """

    def decorator(cls: type[BaseConfig]):
        ConfigRegistry.register(name, cls)
        return cls

    return decorator
