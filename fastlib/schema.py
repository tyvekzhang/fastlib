# SPDX-License-Identifier: MIT
"""Common schema with data validation."""

from typing import Literal

from pydantic import BaseModel


class UserCredential(BaseModel):
    """Represents an authentication user credential with metadata.

    Attributes:
        access_token: JWT access token string.
        expired_in: Access token expiration time, second.
        refresh_token: Token used to refresh access.
    """

    access_token: str
    expired_in: int = 7200
    refresh_token: str


class CurrentUser(BaseModel):
    """Minimal user identity information for authenticated requests.

    Attributes:
        user_id: Unique identifier of the authenticated user.
    """

    user_id: int


class SortItem(BaseModel):
    """Single field sorting specification.

    Attributes:
        field: Name of the field to sort by
        order: Sort direction ('asc' or 'desc')
    """

    field: str
    order: Literal["asc", "desc"]
