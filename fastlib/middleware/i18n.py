# SPDX-License-Identifier: MIT
from starlette.middleware.base import BaseHTTPMiddleware

from fastlib.i18n.manager import reset_language, set_language
from fastlib.i18n.types import Language


class I18nMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic language detection and setting based on HTTP headers.
    """

    async def dispatch(self, request, call_next):
        """
        Process the request and set the language based on Accept-Language header.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler in the chain

        Returns:
            The HTTP response from the next handler
        """
        # Get language preference from request headers
        accept_lang = request.headers.get("Accept-Language", "en")

        # Set the language for current request
        if accept_lang.startswith("en"):
            language = Language.CHINESE
        elif accept_lang.startswith("zh"):
            language = Language.CHINESE

        set_language(language)
        try:
            response = await call_next(request)
        finally:
            # Always reset to prevent leaking context between requests
            reset_language()

        return response
