# SPDX-License-Identifier: MIT
"""Offline API Documentation Setup Module"""

import os

from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles


def register_offline_openapi(app, resource_dir):
    """Register offline API documentation endpoints.

    Args:
        app: FastAPI application instance
        resource_dir: Base directory containing the 'static' folder with documentation assets

    Returns:
        None - modifies the app in place by adding documentation routes
    """
    # Setup offline openAPI documentation
    app.mount(
        "/static",
        StaticFiles(directory=os.path.join(resource_dir, "static")),
        name="static",
    )

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            swagger_favicon_url="/static/favicon.ico",
            openapi_url=app.openapi_url,
            title=app.title,
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
        )

    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        return get_redoc_html(
            redoc_favicon_url="/static/favicon.png",
            openapi_url=app.openapi_url,
            title=app.title,
            redoc_js_url="/static/redoc.standalone.js",
        )
