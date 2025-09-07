# SPDX-License-Identifier: MIT
"""Configuration loading and management with dynamic registry support."""

import os
from functools import lru_cache
from typing import Optional

from fastlib import constant
from fastlib.config.config import Config
from fastlib.config.config_loader import ConfigLoader
from fastlib.config.config_registry import BaseConfig, ConfigRegistry
from fastlib.config.database_config import DatabaseConfig
from fastlib.config.security_config import SecurityConfig
from fastlib.config.server_config import ServerConfig

config: Config


@lru_cache
def load_config() -> Config:
    """
    Loads the configuration based on the provided command-line arguments.

    Returns:
        Config: A configuration object populated with the loaded settings.
    """
    global config
    env = os.getenv(constant.ENV, "dev")

    config_file = os.getenv(constant.CONFIG_FILE, None)
    config_loader = ConfigLoader(env, config_file)
    config_dict = config_loader.load_config()
    config = Config(config_dict)
    return config


@lru_cache
def load_server_config() -> ServerConfig:
    """
    Loads and returns the server configuration.

    Returns:
        ServerConfig: The server configuration object.
    """
    config_data = load_config()
    return config_data.server


@lru_cache
def load_database_config() -> DatabaseConfig:
    """
    Loads and returns the database configuration.

    Returns:
        DatabaseConfig: The database configuration object.
    """
    config_data = load_config()
    return config_data.database


@lru_cache
def load_security_config() -> SecurityConfig:
    """
    Loads and returns the security configuration.

    Returns:
        SecurityConfig: The security configuration object.
    """
    config_data = load_config()
    return config_data.security


def get_database_url(*, env: str = "dev"):
    """
    Retrieves the database URL from the configuration file for the specified environment.

    Returns:
        str: The database URL string from the configuration file.
    """

    assert env in ("dev", "prod", "local")
    config_path = os.path.join(constant.RESOURCE_DIR, f"config-{env}.yml")
    config_dict = ConfigLoader.load_yaml_file(config_path)
    if "database" not in config_dict:
        raise ValueError(
            f"database config not in: {env}",
        )
    return config_dict["database"]["url"]


def register_config_class(name: str, config_class: type) -> None:
    """
    Register a new configuration class dynamically.

    Args:
        name: The name to register the configuration under
        config_class: The configuration class to register

    Raises:
        ValueError: If the configuration class doesn't inherit from BaseConfig
    """
    if not issubclass(config_class, BaseConfig):
        raise ValueError(
            f"Configuration class {config_class.__name__} must inherit from BaseConfig"
        )

    ConfigRegistry.register(name, config_class)


def create_config_instance(name: str, config_data: dict) -> Optional[BaseConfig]:
    """
    Create an instance of a registered configuration class.

    Args:
        name: The name of the configuration class
        config_data: Configuration data dictionary

    Returns:
        Configuration instance or None if creation failed
    """
    return ConfigRegistry.create_instance(name, {name: config_data})


def list_available_configs() -> list[str]:
    """
    List all registered configuration classes.

    Returns:
        List of registered configuration names
    """
    return ConfigRegistry.list_registered()
