# SPDX-License-Identifier: MIT
"""FastAPI server with lifespan management and global configuration initialization."""

import os
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI
from loguru import logger

from fastlib.config.config_manager import ConfigManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    
    Handles startup and shutdown events for the application.
    """
    # Startup
    logger.info("Starting FastAPI application...")
    
    # Initialize global configuration
    try:
        # Get custom configurations from environment or app state
        custom_configs = getattr(app.state, 'custom_configs', None)
        env = getattr(app.state, 'env', None)
        config_file = getattr(app.state, 'config_file', None)
        
        # Initialize global configuration with optional custom configs
        ConfigManager.initialize_global_config(
            env=env,
            config_file=config_file,
            custom_configs=custom_configs
        )
        
        logger.info("Global configuration initialized successfully")
        
        # Add any custom configuration classes that were registered
        if hasattr(app.state, 'additional_configs'):
            for name, config_instance in app.state.additional_configs.items():
                ConfigManager.add_custom_config(name, config_instance)
                logger.info(f"Added custom configuration: {name}")
        
        # Log configuration status
        config = ConfigManager.get_config()
        logger.info(f"Available configurations: {config.list_configs()}")
        
        # Additional startup tasks can be added here
        logger.info("Application startup complete")
        
    except Exception as e:
        logger.error(f"Failed to initialize configuration: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application...")
    
    # Cleanup tasks can be added here
    ConfigManager.reset()
    logger.info("Application shutdown complete")


def create_app(
    custom_configs: Optional[Dict[str, Any]] = None,
    env: Optional[str] = None,
    config_file: Optional[str] = None,
    additional_configs: Optional[Dict[str, Any]] = None,
    **app_kwargs
) -> FastAPI:
    """
    Create FastAPI application with configuration initialization.
    
    Args:
        custom_configs: Custom configuration data to merge with loaded config
        env: Environment name (dev, prod, local)
        config_file: Custom config file path
        additional_configs: Additional configuration instances to register
        **app_kwargs: Additional arguments passed to FastAPI constructor
        
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    # Create FastAPI app with lifespan
    app = FastAPI(lifespan=lifespan, **app_kwargs)
    
    # Store configuration parameters in app state for lifespan access
    app.state.custom_configs = custom_configs
    app.state.env = env
    app.state.config_file = config_file
    app.state.additional_configs = additional_configs or {}
    
    return app


def create_production_app() -> FastAPI:
    """
    Create a production-ready FastAPI application.
    
    Returns:
        FastAPI: Production configured application
    """
    return create_app(
        title="FastLib Application",
        description="Production FastAPI application with FastLib",
        version="1.0.0",
        docs_url="/docs" if os.getenv("ENABLE_DOCS", "false").lower() == "true" else None,
        redoc_url="/redoc" if os.getenv("ENABLE_DOCS", "false").lower() == "true" else None,
    )


def create_development_app() -> FastAPI:
    """
    Create a development FastAPI application with debug features.
    
    Returns:
        FastAPI: Development configured application
    """
    return create_app(
        title="FastLib Development Application",
        description="Development FastAPI application with FastLib",
        version="1.0.0-dev",
        debug=True,
        docs_url="/docs",
        redoc_url="/redoc",
    )


# Example usage for adding custom configurations
class CustomConfig:
    """Example custom configuration class."""
    
    def __init__(self, feature_enabled: bool = True, max_items: int = 100):
        self.feature_enabled = feature_enabled
        self.max_items = max_items
    
    def __str__(self) -> str:
        return f"CustomConfig(feature_enabled={self.feature_enabled}, max_items={self.max_items})"


def create_app_with_custom_config() -> FastAPI:
    """
    Example of creating an app with custom configuration.
    
    Returns:
        FastAPI: Application with custom configuration
    """
    # Create custom configuration instance
    custom_config = CustomConfig(feature_enabled=True, max_items=200)
    
    # Create app with custom configuration
    app = create_app(
        title="FastLib App with Custom Config",
        additional_configs={"custom": custom_config}
    )
    
    return app


# Convenience function to get the current configuration in route handlers
def get_current_config():
    """
    Get the current global configuration.
    
    Returns:
        Config: Current global configuration instance
        
    Raises:
        RuntimeError: If configuration is not initialized
    """
    return ConfigManager.get_config()


def get_server_config():
    """Get server configuration."""
    return ConfigManager.get_server_config()


def get_database_config():
    """Get database configuration."""
    return ConfigManager.get_database_config()


def get_security_config():
    """Get security configuration."""
    return ConfigManager.get_security_config()