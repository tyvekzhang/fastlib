# SPDX-License-Identifier: MIT
"""
Log configuration and logging utility for the application.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional
from fastlib.config.base import BaseConfig
from fastlib.config.manager import config_class
from fastlib.config.utils import ProjectInfo


LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


@config_class("log")
@dataclass
class LogConfig(BaseConfig):
    """
    Configuration for logging settings.
    """

    log_dir: str = "logs"
    app_name: Optional[str] = None
    log_level: LogLevel = "INFO"
    log_rotation: str = "1 day"
    log_retention: str = "90 days"
    enable_console_log: bool = True
    enable_json_logs: bool = False
    error_log_rotation: str = "1 day"
    error_log_retention: str = "90 days"
    enable_async: bool = True
    max_file_size: Optional[str] = "10 MB"
    time_format: str = "%Y-%m-%d"

    def __post_init__(self):
        """
        Post-initialization hook.
        """
        if not self.app_name:
            project = ProjectInfo.from_pyproject()
            self.app_name = getattr(project, "name", "app")

        # ✅ ensure log directory exists
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)

    @property
    def default_format(self) -> str:
        """Default text log format."""
        return "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"

    @property
    def log_file_name(self) -> str:
        """Main log filename."""
        return f"{self.app_name}.log"

    @property
    def error_log_file_name(self) -> str:
        """Error log filename."""
        return f"{self.app_name}_error.log"

    @property
    def log_file_path(self) -> Path:
        """Full path for the main log file."""
        return Path(self.log_dir) / self.log_file_name

    @property
    def error_log_file_path(self) -> Path:
        """Full path for the error log file."""
        return Path(self.log_dir) / self.error_log_file_name
