# SPDX-License-Identifier: MIT
"""Configuration loading and management with dynamic registry support."""

import os
from typing import Any

from fastlib import constants as constant
from fastlib.config import utils as config_util
from fastlib.config._database_config import DatabaseConfig
from fastlib.config._log_config import LogConfig
from fastlib.config._security_config import SecurityConfig
from fastlib.config._server_config import ServerConfig
from fastlib.config.base import BaseConfig
from fastlib.config.loader import ConfigLoader
from fastlib.config.registry import ConfigRegistry


class ConfigManager:
    """Global configuration manager with static methods and dynamic registry support."""

    _global_config_dict: dict[str, Any] | None = None
    _config_instances: dict[str, BaseConfig] = {}
    _initialized: bool = False

    @staticmethod
    def register_custom_configs(module) -> None:
        """
        Discover and register all custom classes.

        Args:
            module: The Python module to search for config classes
        """
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, BaseConfig):
                if getattr(attr, "__is_config_class__", False):
                    name = getattr(attr, "__config_name__", None)
                    if name:
                        try:
                            ConfigRegistry.register(name, attr)
                        except ValueError:
                            pass

    @staticmethod
    def initialize_global_config(
        env: str | None = None,
        config_file: str | None = None,
        custom_configs: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize global configuration.

        Args:
            env: Environment name (dev, prod, local)
            config_file: Custom config file path
            custom_configs: Custom configuration data to merge
        """
        if ConfigManager._initialized:
            return

        if env is None:
            env = os.getenv(constant.ENV, "dev")

        if config_file is None:
            config_file = os.getenv(constant.CONFIG_FILE, None)

        config_loader = ConfigLoader(env, config_file)
        config_dict = config_loader.load_config()

        # Merge custom configurations if provided
        if custom_configs:
            config_dict = config_util.deep_merge_dict(config_dict, custom_configs)

        ConfigManager._global_config_dict = config_dict

        # Register default configurations if not already registered
        ConfigManager._register_default_configs()

        # Initialize all registered configurations
        ConfigManager._initialize_configs()

        ConfigManager._initialized = True

    @staticmethod
    def _register_default_configs() -> None:
        """Register default configuration classes if not already registered."""
        default_configs = {
            "server": ServerConfig,
            "database": DatabaseConfig,
            "security": SecurityConfig,
            "log": LogConfig,
        }

        for name, config_class in default_configs.items():
            try:
                ConfigRegistry.register(name, config_class)
            except ValueError:
                # Already registered, skip
                pass

    @staticmethod
    def _initialize_configs() -> None:
        """Initialize all registered configuration classes."""
        for config_name in ConfigRegistry.list_registered():
            config_data = ConfigManager._global_config_dict.get(config_name, {})

            try:
                instance = ConfigRegistry.create_instance(
                    config_name, {config_name: config_data}
                )
                if not instance:
                    raise ValueError(f"Config instance for {config_name} returned None")
                ConfigManager._config_instances[config_name] = instance
            except Exception as e:
                raise ValueError(
                    f"Failed to initialize {config_name} config: {e}"
                ) from e

    @staticmethod
    def get_config_instance(config_name: str) -> BaseConfig | None:
        """
        Get a specific configuration instance.

        Args:
            config_name: Name of the configuration to retrieve

        Returns:
            BaseConfig: The configuration instance or None if not found

        Raises:
            RuntimeError: If configuration is not initialized
        """
        if not ConfigManager._initialized:
            raise RuntimeError(
                "Configuration not initialized. Call ConfigManager.initialize_global_config() first."
            )
        return ConfigManager._config_instances.get(config_name)

    @staticmethod
    def get_server_config() -> ServerConfig:
        """
        Get the server configuration.

        Returns:
            ServerConfig: The server configuration object
        """
        instance = ConfigManager.get_config_instance("server")
        if not isinstance(instance, ServerConfig):
            raise RuntimeError("Server configuration not properly initialized")
        return instance

    @staticmethod
    def get_database_config() -> DatabaseConfig:
        """
        Get the database configuration.

        Returns:
            DatabaseConfig: The database configuration object
        """
        instance = ConfigManager.get_config_instance("database")
        if not isinstance(instance, DatabaseConfig):
            raise RuntimeError("Database configuration not properly initialized")
        return instance

    @staticmethod
    def get_security_config() -> SecurityConfig:
        """
        Get the security configuration.

        Returns:
            SecurityConfig: The security configuration object
        """
        instance = ConfigManager.get_config_instance("security")
        if not isinstance(instance, SecurityConfig):
            raise RuntimeError("Security configuration not properly initialized")
        return instance

    @staticmethod
    def get_log_config() -> LogConfig:
        """
        Get the log configuration.

        Returns:
            LogConfig: The log configuration object
        """
        instance = ConfigManager.get_config_instance("log")
        if not isinstance(instance, LogConfig):
            raise RuntimeError("Log configuration not properly initialized")
        return instance

    @staticmethod
    def is_initialized() -> bool:
        """
        Check if the configuration manager is initialized.

        Returns:
            bool: True if initialized, False otherwise
        """
        return ConfigManager._initialized

    @staticmethod
    def get_config_dict() -> dict[str, Any] | None:
        """
        Get the raw configuration dictionary.

        Returns:
            The configuration dictionary or None if not initialized
        """
        return ConfigManager._global_config_dict
