# SPDX-License-Identifier: MIT
"""
A comprehensive logging tool for the application.
"""

import sys
import logging
import logging.config
from pathlib import Path
from typing import Dict, Any, Optional
from logging.handlers import TimedRotatingFileHandler
import json
import gzip
import os
import re

from fastlib._logging.config import LogConfig
from fastlib.config.manager import ConfigManager


class JSONFormatter(logging.Formatter):
    """Custom formatter for JSON logs."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Safely merge user-provided data
        extra_data = getattr(record, "extra_data", None)
        if isinstance(extra_data, dict):
            log_data.update(extra_data)

        return json.dumps(log_data, ensure_ascii=False)


class Logger:
    """
    Enhanced logging tool supporting structured and JSON logs.
    """

    _instances: Dict[str, "Logger"] = {}
    _config: Optional[LogConfig] = None
    _is_configured: bool = False
    _initialized_loggers: set[str] = set()

    @classmethod
    def initialize(cls) -> "Logger":
        """Initialize the logging system."""
        if not cls._is_configured:
            cls._config = cls._get_config()
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
    def get_instance(cls, name: Optional[str] = None) -> "Logger":
        """Get or create a named logger instance."""
        if cls._config is None:
            cls._config = cls._get_config()

        name = name or cls._config.app_name

        if name not in cls._instances:
            cls._instances[name] = cls(name)
        return cls._instances[name]

    def __init__(self, name: str):
        """Initialize the Logger."""
        self.name = name
        self._config = self._get_config()

        # Only setup logging once globally
        if not self.__class__._is_configured:
            self._setup_logging()
            self.__class__._is_configured = True

        # Create or reuse named logger
        self._logger = logging.getLogger(name)

        # Avoid duplicate handler addition
        if name not in self.__class__._initialized_loggers:
            self.__class__._initialized_loggers.add(name)

    # -----------------------------
    # Setup and Handlers
    # -----------------------------

    def _setup_logging(self) -> None:
        """Configure native logging with handlers."""
        config = self._config

        Path(config.log_dir).mkdir(parents=True, exist_ok=True)

        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, config.log_level, logging.INFO))

        # Clear any stale handlers (important for tests)
        for h in root_logger.handlers[:]:
            root_logger.removeHandler(h)
            h.close()

        # Console handler
        if config.enable_console_log:
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setLevel(getattr(logging, config.log_level))
            console_handler.setFormatter(self._get_formatter())
            root_logger.addHandler(console_handler)

        # Main rotating file handler
        file_handler = self._create_file_handler(
            str(config.log_file_path),
            config.log_level,
            config.log_rotation,
            config.log_retention,
        )
        root_logger.addHandler(file_handler)

        # Error log handler
        if config.log_level not in ["ERROR", "CRITICAL"]:
            error_handler = self._create_file_handler(
                str(config.error_log_file_path),
                "ERROR",
                config.error_log_rotation,
                config.error_log_retention,
            )
            root_logger.addHandler(error_handler)

    def _create_file_handler(
        self, filepath: str, level: str, rotation: str, retention: str
    ) -> logging.Handler:
        """Create a TimedRotatingFileHandler with compression."""

        when, interval = self._parse_rotation(rotation)

        handler = TimedRotatingFileHandler(
            filepath,
            when=when,
            interval=interval,
            backupCount=self._parse_retention(retention),
            encoding="utf-8",
            utc=False,
        )

        handler.setLevel(getattr(logging, level, logging.INFO))
        handler.setFormatter(self._get_formatter())

        # Patch doRollover to auto-compress old logs
        original_doRollover = handler.doRollover

        def compressed_doRollover(*args, **kwargs):
            original_doRollover(*args, **kwargs)
            try:
                self._compress_old_logs(filepath)
            except Exception:
                # Prevent logging failure on compression errors
                logging.getLogger(__name__).warning("Log compression failed", exc_info=True)

        handler.doRollover = compressed_doRollover
        return handler

    def _parse_rotation(self, rotation: Optional[str]) -> tuple[str, int]:
        """Parse rotation string like '1 day' or '6 hours'."""
        if not rotation:
            return "midnight", 1
        rotation = rotation.lower()
        num = int(re.findall(r"\d+", rotation)[0]) if re.search(r"\d+", rotation) else 1
        if "hour" in rotation:
            return "h", num
        if "minute" in rotation:
            return "m", num
        return "midnight", num

    def _parse_retention(self, retention: Optional[str]) -> int:
        """Parse retention like '7 days'."""
        if not retention:
            return 7
        if isinstance(retention, (int, float)):
            return int(retention)
        nums = re.findall(r"\d+", str(retention))
        return int(nums[0]) if nums else 7

    def _compress_old_logs(self, base_path: str) -> None:
        """Compress all rotated logs except current."""
        log_dir = os.path.dirname(base_path)
        base_name = os.path.basename(base_path)

        for f in os.listdir(log_dir):
            if f.startswith(base_name) and not f.endswith(".gz"):
                full_path = os.path.join(log_dir, f)
                if f != base_name:  # Skip active file
                    gz_path = f"{full_path}.gz"
                    if not os.path.exists(gz_path):  # avoid double compress
                        with open(full_path, "rb") as f_in, gzip.open(gz_path, "wb") as f_out:
                            f_out.writelines(f_in)
                        os.remove(full_path)

    def _get_formatter(self) -> logging.Formatter:
        """Return JSON or plain formatter."""
        if self._config.enable_json_logs:
            return JSONFormatter()
        return logging.Formatter(self._config.default_format)

    # -----------------------------
    # Logging Methods
    # -----------------------------

    def _log_with_extra(self, level: int, message: str, **kwargs) -> None:
        """Log message with structured context."""
        if not self._logger.isEnabledFor(level):
            return

        # Prevent passing non-serializable extra
        safe_extra = {"extra_data": kwargs}
        self._logger.log(level, message, extra=safe_extra)

    def debug(self, message: str, **kwargs): self._log_with_extra(logging.DEBUG, message, **kwargs)
    def info(self, message: str, **kwargs): self._log_with_extra(logging.INFO, message, **kwargs)
    def warning(self, message: str, **kwargs): self._log_with_extra(logging.WARNING, message, **kwargs)
    def error(self, message: str, **kwargs): self._log_with_extra(logging.ERROR, message, **kwargs)
    def critical(self, message: str, **kwargs): self._log_with_extra(logging.CRITICAL, message, **kwargs)

    def exception(self, message: str, **kwargs):
        """Log exception with traceback."""
        self._logger.exception(message, extra={"extra_data": kwargs})

    @classmethod
    def reset(cls) -> None:
        """Reset all logger instances (for testing)."""
        root_logger = logging.getLogger()
        for h in root_logger.handlers[:]:
            root_logger.removeHandler(h)
            h.close()

        cls._instances.clear()
        cls._config = None
        cls._is_configured = False
        cls._initialized_loggers.clear()
