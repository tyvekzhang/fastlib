# SPDX-License-Identifier: MIT
"""Server configuration for the application."""

from fastlib.config.base import BaseConfig
from fastlib.config.utils import ProjectInfo


class ServerConfig(BaseConfig):
    _project_config = ProjectInfo.from_pyproject()

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 18888,
        name: str = _project_config.name[0].upper() + _project_config.name[1:],
        version: str = _project_config.version,
        app_desc: str = _project_config.description,
        api_prefix: str = "/api",
        debug: bool = False,
        workers: int = 1,
        enable_rate_limit: bool = False,
        global_default_limits: str = "10/second",
    ):
        """
        Initializes server configuration.

        Args:
            host: The server host address.
            port: The server port number.
            name: The server name.
            version: The server version.
            app_desc: The server description.
            api_prefix: The API prefix for routes.
            debug: Whether to enable debug mode.
            workers: The number of worker processes.
            enable_rate_limit: Whether to enable rate limiting.
            global_default_limits: Global rate limit setting.
        """
        self.host = host
        self.port = port
        self.name = name
        self.version = version
        self.app_desc = app_desc
        self.api_prefix = api_prefix
        self.debug = debug
        self.workers = workers
        self.enable_rate_limit = enable_rate_limit
        self.global_default_limits = global_default_limits

    def __str__(self) -> str:
        """
        Returns a string representation of the server configuration.

        Returns:
            A string representation of the ServerConfig instance.
        """
        return f"{self.__class__.__name__}({self.__dict__})"
