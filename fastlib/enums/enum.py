# SPDX-License-Identifier: MIT
"""Enumerations module. Contains commonly used enum types for the application."""

from enum import Enum

from fastlib.enums import ExceptionCode


class SortEnum(str, Enum):
    """Enumeration for sorting directions."""

    ascending = "asc"
    descending = "desc"


class DBTypeEnum(str, Enum):
    """Enumeration for supported database types."""

    PGSQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"


class MediaTypeEnum(str, Enum):
    """Enumeration for media/content types."""

    JSON = ".json"


class CommonErrorCode:
    """Error codes for core domain."""

    INTERNAL_SERVER_ERROR = ExceptionCode(code=-1, message="Internal server exception")
