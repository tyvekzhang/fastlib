# SPDX-License-Identifier: MIT
"""Configuration loading and management with dynamic registry support."""

import os
from typing import Dict, Any, Optional, Type

from fastlib import constant
from fastlib.config.config import BaseConfig
from fastlib.config.loader import ConfigLoader
from fastlib.config.registry import ConfigRegistry
from fastlib.config.database_config import DatabaseConfig
from fastlib.config.security_config import SecurityConfig
from fastlib.config.server_config import ServerConfig


# Decorator for easy registration
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

    def decorator(cls: Type[BaseConfig]):
        ConfigRegistry.register(name, cls)
        return cls

    return decorator

class ConfigManager:
    """Global configuration manager with static methods and dynamic registry support."""
    
    _global_config_dict: Optional[Dict[str, Any]] = None
    _config_instances: Dict[str, BaseConfig] = {}
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
                if instance:
                    ConfigManager._config_instances[config_name] = instance
            except Exception as e:
                # Log error but continue with other configs
                print(f"Warning: Failed to initialize {config_name} config: {e}")
                # Create default instance for critical configs
                if config_name in ["server", "database", "security"]:
                    config_class = ConfigRegistry.get_config_class(config_name)
                    if config_class:
                        default_instance = ConfigManager._create_default_instance(config_class)
                        if default_instance:
                            ConfigManager._config_instances[config_name] = default_instance
    
    @staticmethod
    def _create_default_instance(config_class) -> Optional[BaseConfig]:
        """Create a default instance of a config class."""
        try:
            # Try to create with default parameters
            return config_class()
        except Exception:
            return None
    
    @staticmethod
    def get_config_instance(config_name: str) -> Optional[BaseConfig]:
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
    def add_custom_config(name: str, config_instance: BaseConfig) -> None:
        """
        Add a custom configuration to the global config.
        
        Args:
            name: Configuration name
            config_instance: Configuration instance
        """
        if not ConfigManager._initialized:
            raise RuntimeError(
                "Configuration not initialized. Call ConfigManager.initialize_global_config() first."
            )
        ConfigManager._config_instances[name] = config_instance
    
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
        ConfigManager._global_config_dict = None
        ConfigManager._config_instances.clear()
        ConfigManager._initialized = False
    
    @staticmethod
    def list_config_names() -> list[str]:
        """
        List all available configuration names.
        
        Returns:
            List of configuration names
        """
        if not ConfigManager._initialized:
            return []
        return list(ConfigManager._config_instances.keys())
    
    @staticmethod
    def get_config_dict() -> Optional[Dict[str, Any]]:
        """
        Get the raw configuration dictionary.
        
        Returns:
            The configuration dictionary or None if not initialized
        """
        return ConfigManager._global_config_dict