import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
from app.observability.tracing import get_tracer
from app.observability.logging import logger


class RequestInterceptor(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        trace_id = str(uuid.uuid4())
        request.state.trace_id = trace_id
        request.state.start_time = datetime.utcnow()

        body = None
        if request.method in ("POST", "PUT", "PATCH"):
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body = json.loads(body_bytes)
                    request.state.body = body
            except Exception:
                body = None

        tracer = get_tracer()
        with tracer.start_as_current_span(f"request_{request.method}_{request.url.path}") as span:
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", str(request.url))
            span.set_attribute("trace_id", trace_id)
            span.set_attribute("http.route", request.url.path)

            logger.info(
                "Request intercepted",
                extra={
                    "trace_id": trace_id,
                    "method": request.method,
                    "path": request.url.path,
                    "client_host": request.client.host if request.client else None,
                }
            )

            response = await call_next(request)

            duration = (datetime.utcnow() - request.state.start_time).total_seconds() * 1000
            response.headers["X-Trace-ID"] = trace_id
            response.headers["X-Request-Duration-Ms"] = str(int(duration))

            span.set_attribute("http.status_code", response.status_code)
            span.set_attribute("duration_ms", duration)

            logger.info(
                "Request completed",
                extra={
                    "trace_id": trace_id,
                    "status_code": response.status_code,
                    "duration_ms": duration,
                }
            )

        return response
