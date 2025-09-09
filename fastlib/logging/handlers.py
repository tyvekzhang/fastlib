"""
Logger - A comprehensive logging utility for the application.

This module provides a centralized logging system with correlation ID support,
structured logging, and configurable output handlers.
"""

import sys
import traceback
from pathlib import Path
from typing import Any, Optional, Union

from asgi_correlation_id import correlation_id
from loguru import logger

from fastlib.config.manager import ConfigManager
from fastlib.logging.config import LogConfig


class Logger:
    """
    Enhanced logging utility with correlation ID support and structured logging.
    
    Features:
    - Correlation ID tracking
    - Structured logging
    - Configurable handlers
    - Performance and operation logging
    """
    
    _config: Optional[LogConfig] = None
    
    @classmethod
    def _get_config(cls) -> LogConfig:
        """Lazy load configuration."""
        if cls._config is None:
            config_dict = ConfigManager.get_config_dict().get("log", {})
            cls._config = LogConfig(**config_dict)
        return cls._config
    
    def __init__(
        self,
        log_dir: Optional[Union[str, Path]] = None,
        app_name: Optional[str] = None,
        enable_console: Optional[bool] = None,
        **kwargs
    ):
        """
        Initialize the Logger with optional overrides.
        
        Args:
            log_dir: Directory to store log files
            app_name: Application name for log file naming
            enable_console: Whether to enable console output
            **kwargs: Additional configuration overrides
        """
        config = self._get_config()
        
        # Use provided values or fall back to config
        self.log_dir = Path(log_dir) if log_dir else config.log_dir
        self.app_name = app_name or config.app_name
        self.enable_console = enable_console if enable_console is not None else config.enable_console_log
        
        # Merge additional configuration overrides
        self._config_overrides = kwargs
        
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Configure loguru logger with handlers based on configuration."""
        # Remove default handler
        logger.remove()
        
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        config = self._get_config()
        
        # Console handler
        if self.enable_console:
            logger.add(
                sys.stderr,
                format=self._get_format_string(),
                level=config.log_level,
                colorize=True,
                backtrace=True,
                diagnose=True,
            )
        
        # Main file handler with rotation and retention
        log_file_pattern = self.log_dir / config.log_file_pattern
        
        logger.add(
            str(log_file_pattern),
            format=self._get_format_string(),
            level=config.log_level,
            rotation=config.log_rotation,
            retention=config.log_retention,
            compression="zip",
            backtrace=True,
            diagnose=True,
            enqueue=True,  # Async logging for better performance
        )
        
        # Separate error log handler
        error_log_pattern = self.log_dir / config.error_log_file_pattern
        
        logger.add(
            str(error_log_pattern),
            format=self._get_format_string(),
            level="ERROR",
            rotation=config.error_log_rotation,
            retention=config.error_log_retention,
            compression="zip",
            backtrace=True,
            diagnose=True,
            enqueue=True,
        )
    
    def _get_format_string(self) -> str:
        """Get the log format string with correlation ID."""
        return (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
            f"[CID:{{extra[correlation_id]}}] | "
            "{name}:{function}:{line} | {message}"
        )
    
    @staticmethod
    def _get_correlation_id() -> str:
        """Get the current correlation ID or return SYSTEM."""
        try:
            return correlation_id.get() or "SYSTEM"
        except Exception:
            return "SYSTEM"
    
    def _bind_logger(self) -> logger:
        """Bind logger with current correlation ID."""
        return logger.bind(correlation_id=self._get_correlation_id())
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message."""
        self._bind_logger().debug(message, **kwargs)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message."""
        self._bind_logger().info(message, **kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message."""
        self._bind_logger().warning(message, **kwargs)
    
    def error(
        self, 
        message: str, 
        exc_info: Optional[Exception] = None, 
        **kwargs: Any
    ) -> None:
        """
        Log an error message with optional exception information.
        """
        if exc_info is not None:
            error_details = self._format_exception_details(message, exc_info)
            self._bind_logger().error(error_details, **kwargs)
        else:
            self._bind_logger().error(message, **kwargs)
    
    def critical(
        self, 
        message: str, 
        exc_info: Optional[Exception] = None, 
        **kwargs: Any
    ) -> None:
        """
        Log a critical error message.
        """
        if exc_info is not None:
            error_details = self._format_exception_details(message, exc_info)
            self._bind_logger().critical(error_details, **kwargs)
        else:
            self._bind_logger().critical(message, **kwargs)
    
    @staticmethod
    def _format_exception_details(message: str, exc_info: Exception) -> str:
        """
        Format exception details for logging.
        """
        exc_type = exc_info.__class__.__name__
        exc_message = str(exc_info)
        
        # Get formatted traceback
        tb_lines = traceback.format_exception(
            type(exc_info), exc_info, exc_info.__traceback__
        )
        stack_trace = "".join(tb_lines).strip()
        
        return (
            f"Error: {message}\n"
            f"Exception: {exc_type}: {exc_message}\n"
            f"Traceback:\n{stack_trace}"
        )


# Create default instance (optional)
log = Logger()

# Alternatively, you can create instances as needed:
# log = Logger(log_dir="my_logs", app_name="myapp", max_retention_days=7)
