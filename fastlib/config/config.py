# SPDX-License-Identifier: MIT
"""Application Configuration with dynamic registry support."""

from typing import Any, Dict, Optional

from fastlib.config.config_registry import BaseConfig, ConfigRegistry
from fastlib.config.database_config import DatabaseConfig
from fastlib.config.security_config import SecurityConfig
from fastlib.config.server_config import ServerConfig


class Config:
    """Dynamic configuration class that uses ConfigRegistry."""

    def __init__(self, config_dict: Dict[str, Any] = None):
        """
        Initialize configuration with dynamic registration support.

        Args:
            config_dict: Dictionary containing configuration data
        """
        if config_dict is None:
            config_dict = {}

        self._config_dict = config_dict
        self._config_instances: Dict[str, BaseConfig] = {}

        # Register default configurations if not already registered
        self._register_default_configs()

        # Initialize all registered configurations
        self._initialize_configs()

    def _register_default_configs(self) -> None:
        """Register default configuration classes if not already registered."""
        default_configs = {
            "server": ServerConfig,
            "database": DatabaseConfig,
            "security": SecurityConfig,
        }

        for name, config_class in default_configs.items():
            try:
                ConfigRegistry.register(name, config_class)
            except ValueError:
                # Already registered, skip
                pass

    def _initialize_configs(self) -> None:
        """Initialize all registered configuration classes."""
        for config_name in ConfigRegistry.list_registered():
            config_data = self._config_dict.get(config_name, {})

            try:
                instance = ConfigRegistry.create_instance(
                    config_name, {config_name: config_data}
                )
                if instance:
                    self._config_instances[config_name] = instance
                    # Set as attribute for backward compatibility
                    setattr(self, config_name, instance)
            except Exception as e:
                # Log error but continue with other configs
                print(f"Warning: Failed to initialize {config_name} config: {e}")
                # Create default instance for critical configs
                if config_name in ["server", "database", "security"]:
                    config_class = ConfigRegistry.get_config_class(config_name)
                    if config_class:
                        default_instance = self._create_default_instance(config_class)
                        if default_instance:
                            self._config_instances[config_name] = default_instance
                            setattr(self, config_name, default_instance)

    def _create_default_instance(self, config_class) -> Optional[BaseConfig]:
        """Create a default instance of a config class."""
        try:
            # Try to create with default parameters
            return config_class()
        except Exception:
            return None

    def get_config(self, name: str) -> Optional[BaseConfig]:
        """
        Get a configuration instance by name.

        Args:
            name: The name of the configuration

        Returns:
            The configuration instance or None if not found
        """
        return self._config_instances.get(name)

    def add_config(self, name: str, config_instance: BaseConfig) -> None:
        """
        Add a configuration instance dynamically.

        Args:
            name: The name of the configuration
            config_instance: The configuration instance to add
        """
        self._config_instances[name] = config_instance
        setattr(self, name, config_instance)

    def list_configs(self) -> list[str]:
        """
        List all available configuration names.

        Returns:
            List of configuration names
        """
        return list(self._config_instances.keys())

    def reload_config(self, name: str, config_data: Dict[str, Any]) -> bool:
        """
        Reload a specific configuration with new data.

        Args:
            name: The name of the configuration to reload
            config_data: New configuration data

        Returns:
            True if successful, False otherwise
        """
        try:
            instance = ConfigRegistry.create_instance(name, {name: config_data})
            if instance:
                self._config_instances[name] = instance
                setattr(self, name, instance)
                return True
        except Exception as e:
            print(f"Failed to reload {name} config: {e}")
        return False

    def __str__(self) -> str:
        """
        Returns a string representation of the configuration.

        Returns:
            A string representation of the config instance.
        """
        configs_str = {
            name: str(config) for name, config in self._config_instances.items()
        }
        return f"{self.__class__.__name__}({configs_str})"
