"""FastAPI Middleware: Request ID tracing, security headers, error envelope (SPEC §13.3)."""

from __future__ import annotations

import logging
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("kairos.api")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response: Response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self' ws: wss:; frame-ancestors 'none'; base-uri 'none';"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"

        # Permissions-Policy scoped to demo page / UI; restricted on API endpoints (SPEC §13.3)
        path = request.url.path
        if path == "/" or path.startswith("/demo") or not path.startswith("/v1"):
            response.headers["Permissions-Policy"] = "microphone=(self)"
        else:
            response.headers["Permissions-Policy"] = "microphone=()"

        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        return response


class RequestTracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
