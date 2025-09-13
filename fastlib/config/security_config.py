# SPDX-License-Identifier: MIT
"""Security configuration for the application."""

import os

from fastlib.config.base import BaseConfig


class SecurityConfig(BaseConfig):
    def __init__(
        self,
        enable: bool = True,
        algorithm: str = "HS256",
        secret_key: str = "your-secret-key-change-in-production",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_minutes: int = 60 * 24 * 7,  # 7 days
        enable_swagger: bool = False,
        white_list_routes: str = "/api/v1/probe/liveness, /api/v1/user/register, /api/v1/auth:signInWithEmailAndPassword",
        backend_cors_origins: str = " http://127.0.0.1:8000, http://localhost:8000, http://localhost",
        black_ip_list: str = "",
    ) -> None:
        """
        Initializes security configuration.

        Args:
            enable: Whether to enable security features. Default: True.
            algorithm: The encryption algorithm used for token generation. Default: HS256.
            secret_key: The secret key used for signing the tokens. Default: placeholder.
            access_token_expire_minutes: Minutes until access token expires. Default: 30.
            refresh_token_expire_minutes: Minutes until refresh token expires. Default: 10080 (7 days).
            enable_swagger: Whether to enable swagger UI. Default: False.
            white_list_routes: Comma-separated routes accessible without authentication.
                             Default: API docs and health endpoints.
            backend_cors_origins: Comma-separated list of allowed CORS origins.
                                 Default: Local development addresses.
            black_ip_list: Comma-separated list of blocked IP addresses. Default: empty.
        """
        self.enable = enable
        self.algorithm = algorithm

        # Prioritize environment variable for secret key
        env_secret_key = os.getenv("SECRET_KEY")
        self.secret_key = env_secret_key if env_secret_key is not None else secret_key

        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_minutes = refresh_token_expire_minutes
        self.enable_swagger = enable_swagger
        self.white_list_routes = white_list_routes
        self.backend_cors_origins = backend_cors_origins
        self.black_ip_list = black_ip_list

    @property
    def white_list_routes_list(self) -> list[str]:
        """Returns white list routes as a list."""
        return [
            route.strip()
            for route in self.white_list_routes.split(",")
            if route.strip()
        ]

    @property
    def backend_cors_origins_list(self) -> list[str]:
        """Returns CORS origins as a list."""
        return [
            origin.strip()
            for origin in self.backend_cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def black_ip_list_list(self) -> list[str]:
        """Returns blacklisted IPs as a list."""
        return [ip.strip() for ip in self.black_ip_list.split(",") if ip.strip()]

    def __str__(self) -> str:
        """
        Returns a string representation of the security configuration.

        Returns:
            A string representation of the SecurityConfig instance.
        """
        # Hide secret key in string representation for security
        safe_dict = self.__dict__.copy()
        if "secret_key" in safe_dict:
            safe_dict["secret_key"] = "***" if safe_dict["secret_key"] else ""
        return f"{self.__class__.__name__}({safe_dict})"
