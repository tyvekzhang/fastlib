# SPDX-License-Identifier: MIT
"""
Log configuration and logging utility for the application.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from fastlib.config.base import BaseConfig
from fastlib.config.manager import config_class
from fastlib.config.utils import ProjectInfo

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


@config_class("log")
@dataclass
class LogConfig(BaseConfig):
    """
    Configuration for logging settings.

    Attributes:
        log_dir (str): Directory where log files will be stored.
        app_name (str): Name of the application for log file naming.
        log_level (LogLevel): Minimum log level to record. Possible values: DEBUG, INFO, WARNING, ERROR, CRITICAL.
        log_rotation (str): Frequency of log file rotation. Default is "1 day".
        log_retention (str): How long to keep log files. Default is "90 days".
        enable_console_log (bool): Whether to output logs to console. Default is True.
        enable_json_logs (bool): Whether to use JSON format for logs. Default is False.
        error_log_rotation (str): Frequency of error log rotation. Default is "1 day".
        error_log_retention (str): How long to keep error log files. Default is "90 days".
        enable_async (bool): Whether to use asynchronous logging. Default is True.
        max_file_size (Optional[str]): Maximum size for log files before rotation. Default is "10 MB".
        time_format (str): Format string for timestamps in log file names. Default is "YYYY-MM-DD".
    """

    log_dir: str = "/var/log"
    app_name: str | None = None
    log_level: LogLevel = "INFO"
    log_rotation: str = "1 day"
    log_retention: str = "90 days"
    enable_console_log: bool = True
    enable_json_logs: bool = False
    error_log_rotation: str = "1 day"
    error_log_retention: str = "90 days"
    enable_async: bool = True
    max_file_size: str | None = "10 MB"
    time_format: str = "YYYY-MM-DD"

    def __post_init__(self):
        """
        Set default app_name if not provided.

        If `app_name` is not provided, it will be set to the name of the project
        retrieved from the `pyproject.toml` file.
        """
        if self.app_name is None:
            self.app_name = ProjectInfo.from_pyproject().name

    @property
    def default_format(self) -> str:
        """
        Default log format string.

        Returns:
            str: The default format used for log messages.
        """
        return "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}"

    @property
    def log_file_pattern(self) -> str:
        """
        Returns the main log file pattern with timestamp.

        Returns:
            str: The pattern used to name the main log file.
        """
        return f"{{time:{self.time_format}}}_{self.app_name}.log"

    @property
    def error_log_file_pattern(self) -> str:
        """
        Returns the error log file pattern with timestamp.

        Returns:
            str: The pattern used to name the error log file.
        """
        return f"{{time:{self.time_format}}}_error_{self.app_name}.log"

    @property
    def log_file_path(self) -> Path:
        """
        Returns the full path for the main log file.

        Returns:
            Path: The full path to the main log file.
        """
        return Path(self.log_dir) / self.log_file_pattern

    @property
    def error_log_file_path(self) -> Path:
        """
        Returns the full path for the error log file.

        Returns:
            Path: The full path to the error log file.
        """
        return Path(self.log_dir) / self.error_log_file_pattern
