# SPDX-License-Identifier: MIT
"""Enumerations module. Contains commonly used enum types for the application."""

from enum import Enum


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

    # === Text Formats ===
    JSON = "application/json"
    JSON_PATCH = "application/json-patch+json"
    XML = "application/xml"
    HTML = "text/html"
    TEXT = "text/plain"
    CSS = "text/css"
    JAVASCRIPT = "application/javascript"
    CSV = "text/csv"
    YAML = "application/yaml"
    YML = "application/yaml"  # Alias

    # === Form Data ===
    FORM_URL_ENCODED = "application/x-www-form-urlencoded"
    MULTIPART_FORM = "multipart/form-data"

    # === Binary/Data Formats ===
    PDF = "application/pdf"
    ZIP = "application/zip"
    GZIP = "application/gzip"
    OCTET_STREAM = "application/octet-stream"

    # === Images ===
    PNG = "image/png"
    JPEG = "image/jpeg"
    JPG = "image/jpeg"  # Alias
    GIF = "image/gif"
    WEBP = "image/webp"
    SVG = "image/svg+xml"

    # === Audio ===
    MP3 = "audio/mpeg"
    WAV = "audio/wav"
    WEBM_AUDIO = "audio/webm"

    # === Video ===
    MP4 = "video/mp4"
    WEBM_VIDEO = "video/webm"
    MPEG = "video/mpeg"

    # === Protobuf & Other Binary Formats ===
    PROTOBUF = "application/protobuf"
    MSGPACK = "application/msgpack"
    CBOR = "application/cbor"

    def __str__(self) -> str:
        return self.value
