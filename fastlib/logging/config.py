# SPDX-License-Identifier: MIT
"""Log configuration and logging utility for the application."""

from pathlib import Path
from typing import Literal, Optional

from fastlib.config.base import BaseConfig
from fastlib.config.manager import config_class
from fastlib.config.utils import ProjectInfo

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


@config_class("log")
class LogConfig(BaseConfig):
    """Configuration for logging settings."""

    _project_config = ProjectInfo.from_pyproject()

    def __init__(
        self,
        log_dir: str,
        log_level: LogLevel = "INFO",
        log_rotation: str = "1 day",
        log_retention: str = "7 days",
        log_format: Optional[str] = None,
        time_format: str = "YYYY-MM-DD",
        enable_console_log: bool = True,
        error_log_rotation: str = "1 day",
        error_log_retention: str = "30 days",
        app_name: Optional[str] = None,
        enable_json_logs: bool = False,
        enable_async: bool = True,
        max_file_size: Optional[str] = None,
    ):
        """
        Initializes log configuration.
        """
        self.log_dir = Path(log_dir)
        self.log_level = log_level
        self.log_rotation = log_rotation
        self.log_retention = log_retention
        self.log_format = log_format or self._default_format
        self.time_format = time_format
        self.enable_console_log = enable_console_log
        self.error_log_rotation = error_log_rotation
        self.error_log_retention = error_log_retention
        self.app_name = app_name or self._project_config.name
        self.enable_json_logs = enable_json_logs
        self.enable_async = enable_async
        self.max_file_size = max_file_size

    @property
    def _default_format(self) -> str:
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

    def __str__(self) -> str:
        """
        Returns a string representation of the database configuration.

        Returns:
            A string representation of the DatabaseConfig instance.
        """
        return f"{self.__class__.__name__}({self.__dict__})"
