# SPDX-License-Identifier: MIT
"""
Log configuration and logging utility for the application.
"""

from pathlib import Path
from typing import Literal, Optional

from fastlib.config.base import BaseConfig
from fastlib.config.manager import config_class
from fastlib.config.utils import ProjectInfo

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


@config_class("log")
class LogConfig(BaseConfig):
    """Configuration for logging settings."""

    def __init__(
        self,
        log_dir: str = "/var/log",
        app_name: str = None,
        log_level: LogLevel = "INFO",
        log_rotation: str = "1 day",
        log_retention: str = "90 days",
        enable_console_log: bool = True,
        enable_json_logs: bool = False,
        error_log_rotation: str = "1 day",
        error_log_retention: str = "90 days",
        enable_async: bool = True,
        max_file_size: Optional[str] = "10 MB",
        time_format: str = "YYYY-MM-DD",
        **kwargs,
    ):
        """
        Initialize LogConfig with logging settings.

        Args:
            log_dir: Directory where log files will be stored
            app_name: Name of the application for log file naming
            log_level: Minimum log level to record
            log_rotation: How often to rotate log files
            log_retention: How long to keep log files
            enable_console_log: Whether to output logs to console
            enable_json_logs: Whether to use JSON format for logs
            error_log_rotation: How often to rotate error log files
            error_log_retention: How long to keep error log files
            enable_async: Whether to use asynchronous logging
            max_file_size: Maximum size for log files before rotation
            time_format: Format string for timestamps in log file names
            **kwargs: Additional keyword arguments for base class
        """
        # Set app_name default if not provided
        if app_name is None:
            app_name = ProjectInfo.from_pyproject().name

        # Initialize instance attributes directly
        self.log_dir = log_dir
        self.app_name = app_name
        self.log_level = log_level
        self.log_rotation = log_rotation
        self.log_retention = log_retention
        self.enable_console_log = enable_console_log
        self.enable_json_logs = enable_json_logs
        self.error_log_rotation = error_log_rotation
        self.error_log_retention = error_log_retention
        self.enable_async = enable_async
        self.max_file_size = max_file_size
        self.time_format = time_format

        # Handle any additional kwargs for base class
        if kwargs:
            # If base class needs special handling, you can add it here
            # For now, we'll set them as instance attributes
            for key, value in kwargs.items():
                setattr(self, key, value)

    @property
    def default_format(self) -> str:
        """Default log format string."""
        return "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}"

    @property
    def log_file_pattern(self) -> str:
        """Returns the main log file pattern with timestamp."""
        return f"{{time:{self.time_format}}}_{self.app_name}.log"

    @property
    def error_log_file_pattern(self) -> str:
        """Returns the error log file pattern with timestamp."""
        return f"{{time:{self.time_format}}}_error_{self.app_name}.log"

    @property
    def log_file_path(self) -> Path:
        """Returns the full path for the main log file."""
        return Path(self.log_dir) / self.log_file_pattern

    @property
    def error_log_file_path(self) -> Path:
        """Returns the full path for the error log file."""
        return Path(self.log_dir) / self.error_log_file_pattern
