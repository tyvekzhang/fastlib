# SPDX-License-Identifier: MIT
"""Server configuration for the application."""

from dataclasses import dataclass, field
from typing import ClassVar

from fastlib.config.base import BaseConfig
from fastlib.config.utils import ProjectInfo


@dataclass
class ServerConfig(BaseConfig):
    """
    Server configuration for the application.

    Attributes:
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

    _project_config: ClassVar[ProjectInfo] = ProjectInfo.from_pyproject()

    host: str = "127.0.0.1"
    port: int = 18888
    name: str = field(default_factory=lambda: ServerConfig._get_default_name())
    version: str = field(default_factory=lambda: ServerConfig._project_config.version)
    app_desc: str = field(
        default_factory=lambda: ServerConfig._project_config.description
    )
    api_prefix: str = "/api"
    debug: bool = False
    workers: int = 1
    enable_rate_limit: bool = False
    global_default_limits: str = "10/second"

    @classmethod
    def _get_default_name(cls) -> str:
        """Get the default server name from project config."""
        name = cls._project_config.name
        return name[0].upper() + name[1:] if name else "Server"
