# SPDX-License-Identifier: MIT
"""Configuration registry for dynamic configuration class management."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type


class BaseConfig(ABC):
    """Abstract base class for all configuration classes."""

    @abstractmethod
    def __init__(self, **kwargs):
        """Initialize configuration with keyword arguments."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Return string representation of the configuration."""
        pass


class ConfigRegistry:
    """Registry for managing configuration classes dynamically."""

    _registry: Dict[str, Type[BaseConfig]] = {}
    _instances: Dict[str, BaseConfig] = {}

    @classmethod
    def register(cls, name: str, config_class: Type[BaseConfig]) -> None:
        """
        Register a configuration class.

        Args:
            name: The name to register the configuration under
            config_class: The configuration class to register

        Raises:
            ValueError: If name is already registered or config_class is not a BaseConfig subclass
        """
        if name in cls._registry:
            raise ValueError(f"Configuration '{name}' is already registered")

        if not issubclass(config_class, BaseConfig):
            raise ValueError("Configuration class must inherit from BaseConfig")

        cls._registry[name] = config_class

    @classmethod
    def unregister(cls, name: str) -> None:
        """
        Unregister a configuration class.

        Args:
            name: The name of the configuration to unregister
        """
        cls._registry.pop(name, None)
        cls._instances.pop(name, None)

    @classmethod
    def get_config_class(cls, name: str) -> Optional[Type[BaseConfig]]:
        """
        Get a registered configuration class.

        Args:
            name: The name of the configuration class

        Returns:
            The configuration class or None if not found
        """
        return cls._registry.get(name)

    @classmethod
    def create_instance(
        cls, name: str, config_dict: Dict[str, Any]
    ) -> Optional[BaseConfig]:
        """
        Create an instance of a registered configuration class.

        Args:
            name: The name of the configuration class
            config_dict: Dictionary containing configuration data

        Returns:
            An instance of the configuration class or None if not found
        """
        config_class = cls._registry.get(name)
        if config_class is None:
            return None

        # Extract configuration data for this specific config
        config_data = config_dict.get(name, {})

        try:
            instance = config_class(**config_data)
            cls._instances[name] = instance
            return instance
        except Exception as e:
            raise ValueError(f"Failed to create {name} config instance: {e}")

    @classmethod
    def get_instance(cls, name: str) -> Optional[BaseConfig]:
        """
        Get a cached configuration instance.

        Args:
            name: The name of the configuration

        Returns:
            The cached configuration instance or None if not found
        """
        return cls._instances.get(name)

    @classmethod
    def list_registered(cls) -> list[str]:
        """
        List all registered configuration names.

        Returns:
            List of registered configuration names
        """
        return list(cls._registry.keys())

    @classmethod
    def clear_instances(cls) -> None:
        """Clear all cached configuration instances."""
        cls._instances.clear()

    @classmethod
    def clear_all(cls) -> None:
        """Clear both registry and instances."""
        cls._registry.clear()
        cls._instances.clear()
