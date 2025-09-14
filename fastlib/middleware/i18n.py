# SPDX-License-Identifier: MIT
from starlette.middleware.base import BaseHTTPMiddleware

from fastlib.i18n.types import Language


class I18nMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic language detection and setting based on HTTP headers.
    
    This middleware inspects the Accept-Language header from incoming requests
    and sets the appropriate language in the request state for use throughout
    the application.
    
    The language preference is stored in request.state.language and can be
    accessed in route handlers and other middleware.
    
    Example:
        ```python
        from fastapi import FastAPI, Request
        
        app = FastAPI()
        app.add_middleware(I18nMiddleware)
        
        @app.get("/")
        async def root(request: Request):
            language = request.state.language
            return {"language": language.value}
        ```
    
    Note:
        Currently supports only English and Chinese. Defaults to English
        if the Accept-Language header is not present or unrecognized.
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
            request.state.language = Language.ENGLISH
        else:
            request.state.language = Language.CHINESE

        response = await call_next(request)
        return response