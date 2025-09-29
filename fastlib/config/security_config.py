# SPDX-License-Identifier: MIT
"""Security configuration for the application."""

import os
from dataclasses import dataclass, field
from typing import ClassVar

from fastlib.config.base import BaseConfig


@dataclass
class SecurityConfig(BaseConfig):
    """
    Security configuration for the application.

    Attributes:
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

    enable: bool = True
    algorithm: str = "HS256"
    secret_key: str = field(
        default_factory=lambda: os.getenv(
            "SECRET_KEY", "your-secret-key-change-in-production"
        )
    )
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    enable_swagger: bool = False
    white_list_routes: str = "/api/v1/probe/liveness, /api/v1/user/register, /api/v1/auth:signInWithEmailAndPassword"
    backend_cors_origins: str = (
        "http://127.0.0.1:8000, http://localhost:8000, http://localhost"
    )
    black_ip_list: str = ""

    # Class-level constants for better organization
    _DEFAULT_WHITE_LIST_ROUTES: ClassVar[str] = (
        "/api/v1/probe/liveness, /api/v1/user/register, /api/v1/auth:signInWithEmailAndPassword"
    )
    _DEFAULT_CORS_ORIGINS: ClassVar[str] = (
        "http://127.0.0.1:8000, http://localhost:8000, http://localhost"
    )

    def __post_init__(self) -> None:
        """Post-initialization processing."""
        # Ensure secret_key uses environment variable if available
        env_secret_key = os.getenv("SECRET_KEY")
        if env_secret_key is not None:
            self.secret_key = env_secret_key

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
