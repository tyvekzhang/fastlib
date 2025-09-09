# SPDX-License-Identifier: MIT
"""Configuration registry for dynamic configuration class management."""

from typing import Any, Dict, Optional, Type

# Import BaseConfig from config module to avoid circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastlib.config.config import BaseConfig
else:
    try:
        from fastlib.config.config import BaseConfig
    except ImportError:
        # Fallback for cases where BaseConfig hasn't been defined yet
        BaseConfig = object


class ConfigRegistry:
    """Registry for managing configuration classes dynamically."""

    _registry: Dict[str, Type] = {}
    _instances: Dict[str, Any] = {}

    @classmethod
    def register(cls, name: str, config_class: Type) -> None:
        """
        Register a configuration class.

        Args:
            name: The name to register the configuration under
            config_class: The configuration class to register

        Raises:
            ValueError: If name is already registered
        """
        if name in cls._registry:
            raise ValueError(f"Configuration '{name}' is already registered")

        # Check if BaseConfig is available and if config_class inherits from it
        if hasattr(config_class, '__bases__'):
            from fastlib.config.config import BaseConfig
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
    def get_config_class(cls, name: str) -> Optional[Type]:
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
    ) -> Optional[Any]:
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
    def get_instance(cls, name: str) -> Optional[Any]:
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
