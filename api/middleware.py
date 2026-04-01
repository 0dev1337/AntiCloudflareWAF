from __future__ import annotations

from time import perf_counter

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from core.logging import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = perf_counter()
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"

        try:
            response = await call_next(request)
        except Exception as exc:
            elapsed_ms = (perf_counter() - start_time) * 1000
            logger.error(
                "request_failed method=%s path=%s client=%s duration_ms=%.2f error=%s",
                method,
                path,
                client_ip,
                elapsed_ms,
                exc,
            )
            raise

        elapsed_ms = (perf_counter() - start_time) * 1000
        logger.info(
            "request_completed method=%s path=%s status=%s client=%s duration_ms=%.2f",
            method,
            path,
            response.status_code,
            client_ip,
            elapsed_ms,
        )
        return response


def setup_logging_middleware(app: FastAPI) -> None:
    app.add_middleware(RequestLoggingMiddleware)

