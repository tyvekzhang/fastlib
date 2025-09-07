# SPDX-License-Identifier: MIT
"""Log configuration for the application."""

from pathlib import Path
from fastlib.config.config_registry import BaseConfig
from fastlib.decorator.decorator import config_class
from fastlib.utils.project_config_util import ProjectInfo

@config_class("log")
class LogConfig(BaseConfig):
    project_config = ProjectInfo.from_pyproject()

    def __init__(
        self,
        log_dir: str,
        log_level: str,
        log_rotation: str,
        log_retention: str,
        log_format: str,
        time_format: str,
        enable_console_log: bool,
        error_log_rotation: str,
        error_log_retention: str,
        app_name: str = project_config.name,
    ) -> None:
        """
        Initializes log configuration.

        Args:
            log_dir: Directory to store log files.
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            log_rotation: Log rotation policy (e.g., "10 MB", "1 day").
            log_retention: Log retention period (e.g., "1 week", "30 days").
            log_format: Format string for log messages.
            time_format: Format string for timestamps in logs.
            enable_console_log: Whether to enable console logging.
            error_log_rotation: Error log rotation policy.
            error_log_retention: Error log retention period.
            app_name: The application name for log file naming.
        """
        self.log_dir = Path(log_dir)
        self.log_level = log_level
        self.log_rotation = log_rotation
        self.log_retention = log_retention
        self.log_format = log_format
        self.time_format = time_format
        self.enable_console_log = enable_console_log
        self.error_log_rotation = error_log_rotation
        self.error_log_retention = error_log_retention
        self.app_name = app_name

    @property
    def log_file(self) -> Path:
        """
        Returns the main log file path with timestamp pattern.

        Returns:
            Path object with formatted log file name.
        """
        return self.log_dir / f"{{time:{self.time_format}}}_{self.app_name}.log"

    @property
    def error_log_file(self) -> Path:
        """
        Returns the error log file path with timestamp pattern.

        Returns:
            Path object with formatted error log file name.
        """
        return self.log_dir / f"{{time:{self.time_format}}}_error_{self.app_name}.log"

    def __str__(self) -> str:
        """
        Returns a string representation of the log configuration.

        Returns:
            A string representation of the LogConfig instance.
        """
        return f"{self.__class__.__name__}({self.__dict__})"