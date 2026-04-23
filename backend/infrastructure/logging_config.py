import logging
import json
import time
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from contextlib import asynccontextmanager
import uuid


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, logger: Optional[logging.Logger] = None):
        super().__init__(app)
        self.logger = logger or logging.getLogger("clipsmith.requests")
        self.logger.setLevel(logging.INFO)

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.time()

        log_data = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client_host": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent", ""),
        }

        try:
            response = await call_next(request)

            process_time = time.time() - start_time

            log_data.update(
                {
                    "status_code": response.status_code,
                    "process_time_ms": round(process_time * 1000, 2),
                }
            )

            if response.status_code >= 500:
                self.logger.error("request", extra=log_data)
            elif response.status_code >= 400:
                self.logger.warning("request", extra=log_data)
            else:
                self.logger.info("request", extra=log_data)

            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}s"

            return response

        except Exception as e:
            process_time = time.time() - start_time
            log_data.update(
                {
                    "status_code": 500,
                    "process_time_ms": round(process_time * 1000, 2),
                    "error": str(e),
                }
            )
            self.logger.error("request", extra=log_data, exc_info=e)
            raise


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


def setup_logging(level: str = "INFO") -> None:
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s | %(request_id)s | %(message)s"
    )

    class RequestIdFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            if not hasattr(record, "request_id"):
                record.request_id = "-"
            return True

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(log_format))
    handler.addFilter(RequestIdFilter())

    root_logger = logging.getLogger("clipsmith")
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.handlers = [handler]

    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").handlers = []

    for logger_name in ["sqlalchemy", "sqlmodel"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def logStructured(logger: logging.Logger, level: str, message: str, **kwargs) -> None:
    log_data = {"message": message, **kwargs}
    getattr(logger, level)(message, extra=log_data)
