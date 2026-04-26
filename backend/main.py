from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware
from .presentation.api.video_router import router as video_router
from .presentation.api.auth_router import router as auth_router
from .presentation.api.user_router import router as user_router
from .presentation.api.feed_router import router as feed_router
from .presentation.api.notification_router import router as notification_router
from .presentation.api.hashtag_router import router as hashtag_router
from .presentation.api.moderation_router import router as moderation_router
from .presentation.api.monitoring_router import router as monitoring_router
from .presentation.api.video_editor_router import router as video_editor_router
from .presentation.api.payment_router import router as payment_router
from .presentation.api.analytics_router import router as analytics_router
from .presentation.api.ai_router import router as ai_router
from .presentation.api.community_router import router as community_router
from .presentation.api.social_router import router as social_router
from .presentation.api.engagement_router import router as engagement_router
from .presentation.api.discovery_router import router as discovery_router
from .presentation.api.course_router import router as course_router
from .presentation.api.compliance_router import router as compliance_router
from .presentation.api.push_router import router as push_router
from .presentation.api.two_factor_router import router as two_factor_router
from .presentation.api.watchparty_ws_router import router as watchparty_ws_router
from .presentation.api.effects_router import router as effects_router
from .presentation.middleware.monitoring_middleware import (
    MonitoringMiddleware,
    HealthCheckMiddleware,
    UserActivityMiddleware,
)
from .infrastructure.observability import (
    CorrelationIdMiddleware,
    configure_logging,
    init_otel,
    init_sentry,
)
from .infrastructure.repositories.database import create_db_and_tables
from .infrastructure.logging_config import RequestLoggingMiddleware, setup_logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .infrastructure.config import get_settings
import os

settings = get_settings()

if settings.is_production():
    setup_logging("WARNING")
    configure_logging("WARNING")
else:
    setup_logging("INFO")
    configure_logging("INFO")

init_sentry()

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="clipsmith API", lifespan=lifespan)

# OpenTelemetry — no-op unless OTEL_EXPORTER_OTLP_ENDPOINT is set.
init_otel(app)
# Correlation ID middleware must wrap before security headers so the ID is
# available to subsequent middlewares and downstream handlers.
app.add_middleware(CorrelationIdMiddleware)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # camera+mic must be allowed for first-party so the SPA's recording
        # surface keeps working when co-hosted with the API; geolocation is
        # not used anywhere in the product, keep it disabled.
        response.headers["Permissions-Policy"] = (
            "camera=(self), microphone=(self), geolocation=()"
        )
        # Tight CSP for JSON API responses. The static SPA host (nginx) ships
        # its own CSP for HTML pages — this one applies to /api responses
        # only and stops content sniffing tricks.
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
        )
        if os.getenv("ENVIRONMENT") == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        return response


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(MonitoringMiddleware)
app.add_middleware(HealthCheckMiddleware)
app.add_middleware(UserActivityMiddleware)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS must be added last so it's the outermost middleware
# This ensures CORS headers are added even on error responses
ALLOWED_ORIGINS = settings.allowed_origins.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
)

# Create uploads dir if not exists (redundant with adapter but safe)
os.makedirs("backend/uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="backend/uploads"), name="uploads")

app.include_router(auth_router)
app.include_router(video_router)
app.include_router(user_router)
app.include_router(feed_router)
app.include_router(notification_router)
app.include_router(hashtag_router)
app.include_router(moderation_router)
app.include_router(video_editor_router)
app.include_router(payment_router)
app.include_router(analytics_router)
app.include_router(ai_router)
app.include_router(community_router)
app.include_router(social_router)
app.include_router(engagement_router)
app.include_router(discovery_router)
app.include_router(course_router)
app.include_router(compliance_router)
app.include_router(two_factor_router)
app.include_router(push_router)
app.include_router(watchparty_ws_router)
app.include_router(effects_router)


@app.get("/")
async def root():
    return {"message": "Welcome to clipsmith API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "ok"}
