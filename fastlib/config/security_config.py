# SPDX-License-Identifier: MIT
"""Security configuration for the application."""

import os

from fastlib.config.base import BaseConfig


class SecurityConfig(BaseConfig):
    def __init__(
        self,
        enable: bool,
        enable_swagger: bool,
        algorithm: str,
        secret_key: str,
        access_token_expire_minutes: int,
        refresh_token_expire_minutes: int,
        white_list_routes: str,
        backend_cors_origins: str,
        black_ip_list: str,
    ) -> None:
        """
        Initializes security configuration.

        Args:
            enable: Whether to enable security.
            enable_swagger: Whether to enable swagger ui.
            algorithm: The encryption algorithm used for token generation.
            secret_key: The secret key used for signing the tokens.
            access_token_expire_minutes: The number of minutes until the access token expires.
            refresh_token_expire_minutes: The number of minutes until the refresh token expires.
            white_list_routes: Comma-separated list of routes which can be accessed without authentication.
            backend_cors_origins: Comma-separated list of allowed CORS origins.
            black_ip_list: Comma-separated list of blocked IP addresses.
        """
        self.enable = enable
        self.enable_swagger = enable_swagger
        self.algorithm = algorithm

        # Prioritize environment variable for secret key
        env_secret_key = os.getenv("SECRET_KEY")
        self.secret_key = env_secret_key if env_secret_key is not None else secret_key

        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_minutes = refresh_token_expire_minutes
        self.white_list_routes = white_list_routes
        self.backend_cors_origins = backend_cors_origins
        self.black_ip_list = black_ip_list

    def __str__(self) -> str:
        """
        Returns a string representation of the security configuration.

        Returns:
            A string representation of the SecurityConfig instance.
        """
        return f"{self.__class__.__name__}({self.__dict__})"
