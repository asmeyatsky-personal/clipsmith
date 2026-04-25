"""Observability scaffolding: structured JSON logs, correlation IDs, OTel hooks.

Per Architectural Rules §6.
"""
from __future__ import annotations

import logging
import os
import uuid
from contextvars import ContextVar
from typing import Any

import structlog

correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def _add_correlation_id(_, __, event_dict: dict[str, Any]) -> dict[str, Any]:
    cid = correlation_id_var.get()
    if cid:
        event_dict["correlation_id"] = cid
    return event_dict


def configure_logging(level: str = "INFO") -> None:
    """Wire structlog with JSON renderer + correlation IDs."""
    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            timestamper,
            _add_correlation_id,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        context_class=dict,
        cache_logger_on_first_use=True,
    )


def new_correlation_id() -> str:
    return uuid.uuid4().hex


class CorrelationIdMiddleware:
    """Pure ASGI middleware that ensures every request has a correlation ID."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        # Try inbound header first, else mint a new one.
        headers = dict((k.decode().lower(), v.decode()) for k, v in scope.get("headers", []))
        cid = headers.get("x-correlation-id") or new_correlation_id()
        token = correlation_id_var.set(cid)
        try:
            async def send_with_header(message):
                if message["type"] == "http.response.start":
                    message.setdefault("headers", []).append(
                        (b"x-correlation-id", cid.encode())
                    )
                await send(message)

            await self.app(scope, receive, send_with_header)
        finally:
            correlation_id_var.reset(token)


def init_otel(app) -> None:
    """Wire OpenTelemetry FastAPI instrumentation if available + configured.

    No-op when packages aren't installed (keeps the dep optional in dev).
    """
    if not os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        logging.getLogger(__name__).warning(
            "OTEL packages not installed; skipping tracing wire-up"
        )
        return

    resource = Resource.create({"service.name": os.getenv("OTEL_SERVICE_NAME", "clipsmith-backend")})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)


def init_sentry() -> None:
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
    except ImportError:
        return
    sentry_sdk.init(
        dsn=dsn,
        integrations=[FastApiIntegration()],
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        environment=os.getenv("ENVIRONMENT", "development"),
    )
