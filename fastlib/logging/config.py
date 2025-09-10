# SPDX-License-Identifier: MIT
"""Log configuration and logging utility for the application."""

from pathlib import Path
from dataclasses import dataclass


from fastlib.config.registry import BaseConfig
from fastlib.config.project_config_util import ProjectInfo


@dataclass
class LogConfig(BaseConfig):
    """Configuration for logging settings."""
    
    _project_config = ProjectInfo.from_pyproject()
    
    log_dir: str
    log_level: str = "INFO"
    log_rotation: str = "1 day"
    log_retention: str = "7 days"
    log_format: str = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}"
    time_format: str = "YYYY-MM-DD"
    enable_console_log: bool = True
    error_log_rotation: str = "1 day"
    error_log_retention: str = "30 days"
    app_name: str = _project_config.name
    
    def __post_init__(self):
        """Post-initialization processing."""
        self.log_dir = Path(self.log_dir)
        
    @property
    def log_file_pattern(self) -> str:
        """Returns the main log file pattern with timestamp."""
        return f"{{time:{self.time_format}}}_{self.app_name}.log"
    
    @property
    def error_log_file_pattern(self) -> str:
        """Returns the error log file pattern with timestamp."""
        return f"{{time:{self.time_format}}}_error_{self.app_name}.log"