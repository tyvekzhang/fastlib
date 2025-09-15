# SPDX-License-Identifier: MIT
"""Common module exception"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from jwt import PyJWTError
from pydantic_core._pydantic_core import ValidationError  # noqa
from starlette.exceptions import HTTPException as StarletteHTTPException

from fastlib.exception import exception_handler
from fastlib.exception.base import HTTPException


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers to the FastAPI application"""

    # Register handlers using add_exception_handler method
    app.add_exception_handler(Exception, exception_handler.global_exception_handler)
    app.add_exception_handler(
        ValidationError, exception_handler.validation_exception_handler
    )

    app.add_exception_handler(HTTPException, exception_handler.custom_exception_handler)

    app.add_exception_handler(
        StarletteHTTPException, exception_handler.custom_http_exception_handler
    )
    app.add_exception_handler(
        RequestValidationError,
        exception_handler.request_validation_exception_handler,
    )
    app.add_exception_handler(PyJWTError, exception_handler.jwt_exception_handler)
