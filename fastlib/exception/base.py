# SPDX-License-Identifier: MIT
"""Base exception class for the application."""

from http import HTTPStatus
from typing import Any, Optional

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Error detail."""

    code: int
    message: str


class BaseException(Exception):
    """
    Base exception class for all custom exception in the application.

    Attributes:
        code: The code enum member from BaseErrorCode or its subclasses.
        message: Optional additional message about the error.
        details: Optional extra error details.
    """

    def __init__(
        self,
        code: ErrorDetail,
        message: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        """
        Initialize the HTTPException.

        Args:
            code: The error code enum member.
            message: Optional additional message about the error.
            details: Optional extra error details.
        """
        self.code = code
        self.message = message
        self.details = details
        self.__post_init__()

    def __post_init__(self):
        if self.message is None:
            self.message = self.code.message


class SystemErrorCode:
    """System-related error codes."""

    INTERNAL_ERROR = ErrorDetail(
        code=HTTPStatus.INTERNAL_SERVER_ERROR.value, message="Internal server error"
    )


class SystemException(BaseException):
    code: SystemErrorCode
    message: Optional[str] = None
    details: Optional[Any] = None
