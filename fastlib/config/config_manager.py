# SPDX-License-Identifier: MIT
"""Configuration loading and management with dynamic registry support."""

import os
from typing import Dict, Any, Optional

from fastlib import constant
from fastlib.config.config import Config
from fastlib.config.config_loader import ConfigLoader
from fastlib.config.database_config import DatabaseConfig
from fastlib.config.security_config import SecurityConfig
from fastlib.config.server_config import ServerConfig


class ConfigManager:
    """Global configuration manager with static methods."""
    
    _global_config: Optional[Config] = None
    _initialized: bool = False
    
    @staticmethod
    def initialize_global_config(
        env: Optional[str] = None,
        config_file: Optional[str] = None,
        custom_configs: Optional[Dict[str, Any]] = None
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
            config_dict.update(custom_configs)
            
        ConfigManager._global_config = Config(config_dict)
        ConfigManager._initialized = True
    
    @staticmethod
    def get_config() -> Config:
        """
        Get the global configuration instance.
        
        Returns:
            Config: The global configuration object
            
        Raises:
            RuntimeError: If configuration is not initialized
        """
        if not ConfigManager._initialized or ConfigManager._global_config is None:
            raise RuntimeError(
                "Configuration not initialized. Call ConfigManager.initialize_global_config() first."
            )
        return ConfigManager._global_config
    
    @staticmethod
    def get_server_config() -> ServerConfig:
        """
        Get the server configuration.
        
        Returns:
            ServerConfig: The server configuration object
        """
        config = ConfigManager.get_config()
        return config.server
    
    @staticmethod
    def get_database_config() -> DatabaseConfig:
        """
        Get the database configuration.
        
        Returns:
            DatabaseConfig: The database configuration object
        """
        config = ConfigManager.get_config()
        return config.database
    
    @staticmethod
    def get_security_config() -> SecurityConfig:
        """
        Get the security configuration.
        
        Returns:
            SecurityConfig: The security configuration object
        """
        config = ConfigManager.get_config()
        return config.security
    
    @staticmethod
    def add_custom_config(name: str, config_instance) -> None:
        """
        Add a custom configuration to the global config.
        
        Args:
            name: Configuration name
            config_instance: Configuration instance
        """
        config = ConfigManager.get_config()
        config.add_config(name, config_instance)
    
    @staticmethod
    def is_initialized() -> bool:
        """
        Check if the configuration manager is initialized.
        
        Returns:
            bool: True if initialized, False otherwise
        """
        return ConfigManager._initialized
    
    @staticmethod
    def reset() -> None:
        """
        Reset the configuration manager (mainly for testing).
        """
        ConfigManager._global_config = None
        ConfigManager._initialized = False


# Backward compatibility functions
def load_config() -> Config:
    """
    Loads the configuration based on the provided command-line arguments.
    
    Returns:
        Config: A configuration object populated with the loaded settings.
    """
    if not ConfigManager.is_initialized():
        ConfigManager.initialize_global_config()
    return ConfigManager.get_config()


def load_server_config() -> ServerConfig:
    """
    Loads and returns the server configuration.
    
    Returns:
        ServerConfig: The server configuration object.
    """
    if not ConfigManager.is_initialized():
        ConfigManager.initialize_global_config()
    return ConfigManager.get_server_config()


def load_database_config() -> DatabaseConfig:
    """
    Loads and returns the database configuration.
    
    Returns:
        DatabaseConfig: The database configuration object.
    """
    if not ConfigManager.is_initialized():
        ConfigManager.initialize_global_config()
    return ConfigManager.get_database_config()


def load_security_config() -> SecurityConfig:
    """
    Loads and returns the security configuration.
    
    Returns:
        SecurityConfig: The security configuration object.
    """
    if not ConfigManager.is_initialized():
        ConfigManager.initialize_global_config()
    return ConfigManager.get_security_config()


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