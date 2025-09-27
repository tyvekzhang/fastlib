# SPDX-License-Identifier: MIT
"""
A comprehensive logging tool for the application.
"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from fastlib.config.manager import ConfigManager
from fastlib.logging.config import LogConfig


class Logger:
    """
    Enhanced logging tool support structured logging.
    """

    _instances: dict[str, "Logger"] = {}
    _config: Optional[LogConfig] = None
    _is_configured: bool = False

    @classmethod
    def initialize(cls) -> "Logger":
        """
        Initialize the logging system.

        Returns:
            Logger instance
        """
        if not cls._is_configured:
            # Load configuration first
            cls._config = cls._get_config()
            # Create and configure the logger
            instance = cls.get_instance()
            cls._is_configured = True
            return instance
        return cls.get_instance()

    @classmethod
    def _get_config(cls) -> LogConfig:
        """Lazy load configuration."""
        if cls._config is None:
            cls._config = ConfigManager.get_config_instance("log")
        return cls._config

    @classmethod
    def get_instance(
        cls,
        name: Optional[str] = None,
    ) -> "Logger":
        """
        Get or create a named logger instance.

        Args:
            name: Logger instance name

        Returns:
            Logger instance
        """
        # Ensure config is loaded
        if cls._config is None:
            cls._config = cls._get_config()

        if not name:
            name = cls._config.app_name

        if name not in cls._instances:
            cls._instances[name] = cls(name)
        return cls._instances[name]

    def __init__(self, name: str):
        """Initialize the Logger with optional overrides."""
        self.name = name

        # Get configuration
        self._config = self._get_config()

        # Only setup logging once globally
        if not self.__class__._is_configured:
            self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure loguru logger with handlers based on configuration."""
        # Remove default handler
        logger.remove()

        config = self._config

        # Create log directory
        Path(config.log_dir).mkdir(parents=True, exist_ok=True)

        # Console handler
        if config.enable_console_log:
            logger.add(
                sys.stderr,
                format=self._get_format_string(),
                level=config.log_level,
                colorize=True,
            )

        # Main file handler
        rotation = config.max_file_size or config.log_rotation

        logger.add(
            str(config.log_file_path),
            format=self._get_format_string(),
            level=config.log_level,
            rotation=rotation,
            retention=config.log_retention,
            compression="zip",
            serialize=config.enable_json_logs,
            enqueue=config.enable_async,
        )

        # Error log handler - only add if log level is not ERROR or CRITICAL
        if config.log_level not in ["ERROR", "CRITICAL"]:
            logger.add(
                str(config.error_log_file_path),
                format=self._get_format_string(),
                level="ERROR",
                rotation=config.error_log_rotation,
                retention=config.error_log_retention,
                compression="zip",
                serialize=config.enable_json_logs,
                enqueue=config.enable_async,
            )

    def _get_format_string(self) -> str:
        """Get the log format string."""
        config = self._config

        if config.enable_json_logs:
            # JSON logs don't need format string
            return "{message}"

        return config.default_format

    # Convenience methods for logging
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        logger.bind(logger_name=self.name).debug(message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        logger.bind(logger_name=self.name).info(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        logger.bind(logger_name=self.name).warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        logger.bind(logger_name=self.name).error(message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        logger.bind(logger_name=self.name).critical(message, **kwargs)

    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback."""
        logger.bind(logger_name=self.name).exception(message, **kwargs)

    @classmethod
    def reset(cls) -> None:
        """Reset all logger instances and configuration (useful for testing)."""
        cls._instances.clear()
        cls._config = None
        cls._is_configured = False
        logger.remove()
