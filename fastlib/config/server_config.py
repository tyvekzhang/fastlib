# SPDX-License-Identifier: MIT
"""Server configuration for the application."""

from fastlib.config.config import BaseConfig
from fastlib.config.project_config_util import ProjectInfo


class ServerConfig(BaseConfig):
    project_config = ProjectInfo.from_pyproject()

    def __init__(
        self,
        host: str,
        port: int,
        api_prefix: str,
        workers: int,
        debug: bool,
        log_file_path: str,
        win_tz: str,
        linux_tz: str,
        enable_rate_limit: bool,
        global_default_limits: str,
        name: str = project_config.name[0].upper() + project_config.name[1:],
        version: str = project_config.version,
        app_desc: str = project_config.description,
    ) -> None:
        """
        Initializes server configuration.

        Args:
            host: The server host address.
            name: The server name.
            port: The server port number.
            version: The server version.
            app_desc: The server app_desc.
            api_prefix: The server api_prefix.
            debug: Whether to enable debug mode.
            workers: The server worker numbers.
            log_file_path: Path to the log file.
            win_tz: Windows timezone setting.
            linux_tz: Linux timezone setting.
            enable_rate_limit: Whether to enable rate limiting.
            global_default_limits: Global rate limit setting.
        """
        self.host = host
        self.name = name
        self.port = port
        self.version = version
        self.app_desc = app_desc
        self.api_prefix = api_prefix
        self.debug = debug
        self.workers = workers
        self.log_file_path = log_file_path
        self.win_tz = win_tz
        self.linux_tz = linux_tz
        self.enable_rate_limit = enable_rate_limit
        self.global_default_limits = global_default_limits

    def __str__(self) -> str:
        """
        Returns a string representation of the server configuration.

        Returns:
            A string representation of the ServerConfig instance.
        """
        return f"{self.__class__.__name__}({self.__dict__})"
