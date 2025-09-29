# SPDX-License-Identifier: MIT
"""JWT middleware for FastAPI authentication"""

import http
from enum import Enum

from fastapi import Request
from jwt.exceptions import PyJWTError
from loguru import logger
from starlette.responses import JSONResponse

from fastlib import ConfigManager, constant, security
from fastlib.contextvars import clear_current_user, set_current_user
from fastlib.enums import MediaTypeEnum
from fastlib.schema import UserCredential

# Load configuration
server_config = ConfigManager.get_server_config()
security_config = ConfigManager.get_security_config()


class JWTErrorCode(Enum):
    """Authentication error codes with code and message"""

    OPENAPI_FORBIDDEN = (403, "OpenAPI documentation is disabled")
    TOKEN_EXPIRED = (401, "Authorization token has expired")
    MISSING_TOKEN = (401, "Authorization token is missing")

    def __init__(self, code: int, message: str):
        self._code = code
        self._message = message

    @property
    def code(self) -> int:
        """Get error code"""
        return self._code

    @property
    def message(self) -> str:
        """Get error message"""
        return self._message

    def to_dict(self) -> dict:
        """Convert to dictionary format for JSON response"""
        return {"code": self.code, "message": self.message}


async def jwt_middleware(request: Request, call_next):
    ctx_token: UserCredential | None = None
    try:
        raw_url_path = request.url.path
        if not raw_url_path.__contains__(
            server_config.api_prefix
        ) or raw_url_path.__contains__(MediaTypeEnum.JSON.value):
            if security_config.enable_swagger:
                return await call_next(request)
            else:
                return JSONResponse(
                    status_code=http.HTTPStatus.FORBIDDEN,
                    content={
                        "code": JWTErrorCode.OPENAPI_FORBIDDEN.code,
                        "message": JWTErrorCode.OPENAPI_FORBIDDEN.message,
                    },
                )

        white_list_routes = [
            r.strip() for r in security_config.white_list_routes.split(",")
        ]
        request_url_path = (
            server_config.api_prefix + raw_url_path.split(server_config.api_prefix)[1]
        )
        if request_url_path in white_list_routes:
            return await call_next(request)

        if not security_config.enable:
            return await call_next(request)

        auth_header = request.headers.get(constant.AUTHORIZATION)
        if auth_header:
            try:
                token = auth_header.split(" ")[-1]
                security.validate_token(token)
                user_id = security.get_user_id(token)

                set_current_user(user_id=user_id)

            except PyJWTError as e:
                logger.error(e)
                return JSONResponse(
                    status_code=http.HTTPStatus.UNAUTHORIZED,
                    content={
                        "code": JWTErrorCode.TOKEN_EXPIRED.code,
                        "message": JWTErrorCode.TOKEN_EXPIRED.message,
                    },
                )
        else:
            return JSONResponse(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                content={
                    "code": JWTErrorCode.MISSING_TOKEN.code,
                    "message": JWTErrorCode.MISSING_TOKEN.message,
                },
            )

        response = await call_next(request)
        return response

    finally:
        if ctx_token is not None:
            clear_current_user(ctx_token)
