"""
Logger - A comprehensive logging utility for the application.

This module provides a centralized logging system with correlation ID support,
structured logging, and configurable output handlers.
"""

import sys
import traceback
from pathlib import Path
from typing import Any, Optional

from asgi_correlation_id import correlation_id
from loguru import logger

from fastlib.config.config_manager import load_config


class Logger:
    """
    Enhanced logging utility with correlation ID support and structured logging.

    This class provides a unified interface for logging with automatic
    correlation ID binding and comprehensive error tracking.
    """
    config = load_config()

    def __init__(self, log_dir: str = "/var/log", max_retention_days: int = 30, 
                 app_name: str = "app", enable_console: bool = True):
        """
        Initialize the Logger.

        Args:
            log_dir: Directory to store log files
            max_retention_days: Maximum number of days to retain log files
            app_name: Application name for log file naming
            enable_console: Whether to enable console output
        """
        self.log_dir = Path(log_dir)
        self.max_retention_days = max_retention_days
        self.app_name = app_name
        self.enable_console = enable_console
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure loguru logger with handlers."""
        # Remove default handler
        logger.remove()

        # Create log directory
        self.log_dir.mkdir(exist_ok=True)

        # Terminal handler
        if self.enable_console:
            logger.add(
                sys.stderr,
                format=self._get_format_string(),
                level="INFO",
                colorize=True,
                backtrace=True,
                diagnose=True,
            )

        # File handlers
        log_file = self.log_dir / f"{self.app_name}_{{time:YYYY-MM-DD}}.log"

        # Info level file handler
        logger.add(
            str(log_file),
            format=self._get_format_string(),
            level="INFO",
            rotation="1 day",
            retention=f"{self.max_retention_days} days",
            compression="zip",
            backtrace=True,
            diagnose=True,
        )

        # Error level file handler
        logger.add(
            str(log_file),
            format=self._get_format_string(),
            level="ERROR",
            rotation="1 day",
            retention=f"{self.max_retention_days} days",
            compression="zip",
            backtrace=True,
            diagnose=True,
        )

        # Debug level file handler (optional)
        logger.add(
            str(log_file),
            format=self._get_format_string(),
            level="DEBUG",
            rotation="1 day",
            retention=f"{self.max_retention_days} days",
            compression="zip",
            backtrace=True,
            diagnose=True,
        )

    def _get_format_string(self) -> str:
        """Get the log format string with correlation ID."""
        return "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | [CID:{extra[correlation_id]}] | {name}:{function}:{line} | {message}"

    def _get_correlation_id(self) -> str:
        """Get the current correlation ID or return SYSTEM."""
        try:
            return correlation_id.get() or "SYSTEM"
        except:
            return "SYSTEM"

    def _bind_logger(self):
        """Bind logger with current correlation ID."""
        return logger.bind(correlation_id=self._get_correlation_id())

    def debug(self, message: str, **kwargs: Any) -> None:
        """
        Log a debug message.

        Args:
            message: The message to log
            **kwargs: Additional context data
        """
        self._bind_logger().debug(message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """
        Log an info message.

        Args:
            message: The message to log
            **kwargs: Additional context data
        """
        self._bind_logger().info(message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """
        Log a warning message.

        Args:
            message: The message to log
            **kwargs: Additional context data
        """
        self._bind_logger().warning(message, **kwargs)

    def error(
        self, message: str, exc_info: Optional[Exception] = None, **kwargs: Any
    ) -> None:
        """
        Log an error message with optional exception information.

        Args:
            message: The error message
            exc_info: Optional exception object for detailed error tracking
            **kwargs: Additional context data
        """
        if exc_info is not None:
            error_details = self._format_exception_details(message, exc_info)
            self._bind_logger().error(error_details, **kwargs)
        else:
            self._bind_logger().error(message, **kwargs)

    def critical(
        self, message: str, exc_info: Optional[Exception] = None, **kwargs: Any
    ) -> None:
        """
        Log a critical error message.

        Args:
            message: The critical error message
            exc_info: Optional exception object for detailed error tracking
            **kwargs: Additional context data
        """
        if exc_info is not None:
            error_details = self._format_exception_details(message, exc_info)
            self._bind_logger().critical(error_details, **kwargs)
        else:
            self._bind_logger().critical(message, **kwargs)

    def _format_exception_details(self, message: str, exc_info: Exception) -> str:
        """
        Format exception details for logging.

        Args:
            message: The base error message
            exc_info: The exception object

        Returns:
            Formatted error details string
        """
        exc_type = exc_info.__class__.__name__
        exc_message = str(exc_info)

        # Get stack trace
        stack_trace = []
        if exc_info.__traceback__:
            tb_list = traceback.extract_tb(exc_info.__traceback__)
            for tb in tb_list:
                stack_trace.append(
                    f"File: {tb.filename}, "
                    f"Line: {tb.lineno}, "
                    f"Function: {tb.name}"
                )

        # Format error details
        error_details = [
            f"Error Message: {message}",
            f"Exception Type: {exc_type}",
            f"Exception Details: {exc_message}",
        ]

        if stack_trace:
            error_details.append("Stack Trace:")
            error_details.extend(stack_trace)

        return "\n".join(error_details)

    def log_performance(self, operation: str, duration: float, **kwargs: Any) -> None:
        """
        Log performance metrics.

        Args:
            operation: Name of the operation
            duration: Duration in seconds
            **kwargs: Additional performance metrics
        """
        message = f"Performance: {operation} took {duration:.3f}s"
        if kwargs:
            metrics = ", ".join(f"{k}={v}" for k, v in kwargs.items())
            message += f" | {metrics}"

        self.info(message)

    def log_api_call(
        self, method: str, url: str, status_code: int, duration: float, **kwargs: Any
    ) -> None:
        """
        Log API call details.

        Args:
            method: HTTP method
            url: API endpoint URL
            status_code: HTTP status code
            duration: Request duration in seconds
            **kwargs: Additional context data
        """
        level = "error" if status_code >= 400 else "info"
        message = f"API Call: {method} {url} -> {status_code} ({duration:.3f}s)"
        
        if kwargs:
            details = ", ".join(f"{k}={v}" for k, v in kwargs.items())
            message += f" | {details}"

        if level == "error":
            self.error(message)
        else:
            self.info(message)

    def log_database_operation(
        self, operation: str, table: str, duration: float, **kwargs: Any
    ) -> None:
        """
        Log database operation details.

        Args:
            operation: Database operation (SELECT, INSERT, etc.)
            table: Table name
            duration: Operation duration in seconds
            **kwargs: Additional operation details
        """
        message = f"Database: {operation} on {table} took {duration:.3f}s"
        if kwargs:
            details = ", ".join(f"{k}={v}" for k, v in kwargs.items())
            message += f" | {details}"

        self.info(message)

    def log_event(self, event_type: str, event_data: dict, **kwargs: Any) -> None:
        """
        Log a custom event.

        Args:
            event_type: Type of event
            event_data: Event data dictionary
            **kwargs: Additional context
        """
        data_str = ", ".join(f"{k}={v}" for k, v in event_data.items())
        message = f"Event: {event_type} | {data_str}"
        
        if kwargs:
            context_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
            message += f" | {context_str}"

        self.info(message)


# Create default instance (optional)
log = Logger()

# Alternatively, you can create instances as needed:
# log = Logger(log_dir="my_logs", app_name="myapp", max_retention_days=7)