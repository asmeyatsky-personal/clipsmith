"""Timeout, retry, and circuit-breaker primitives for external calls.

Per Architectural Rules §4: every external call has a timeout and circuit
breaker. No unbounded waits.
"""
from __future__ import annotations

import functools
import logging
import threading
import time
from typing import Callable, ParamSpec, TypeVar

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


class CircuitBreakerOpen(RuntimeError):
    """Raised when a circuit is open and the call is short-circuited."""


class CircuitBreaker:
    """Minimal in-process circuit breaker.

    States: closed (allow), open (reject), half-open (allow one trial).
    After `failure_threshold` consecutive failures, opens for `reset_seconds`.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        reset_seconds: float = 30.0,
    ):
        self._name = name
        self._failure_threshold = failure_threshold
        self._reset_seconds = reset_seconds
        self._failure_count = 0
        self._opened_at: float | None = None
        self._lock = threading.Lock()

    def _is_open(self) -> bool:
        if self._opened_at is None:
            return False
        if time.monotonic() - self._opened_at >= self._reset_seconds:
            # half-open: allow a trial
            return False
        return True

    def call(self, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        with self._lock:
            if self._is_open():
                raise CircuitBreakerOpen(f"Circuit '{self._name}' is OPEN")
        try:
            result = fn(*args, **kwargs)
        except Exception:
            with self._lock:
                self._failure_count += 1
                if self._failure_count >= self._failure_threshold:
                    self._opened_at = time.monotonic()
                    logger.warning(
                        "Circuit '%s' OPENED after %d failures",
                        self._name,
                        self._failure_count,
                    )
            raise
        with self._lock:
            self._failure_count = 0
            self._opened_at = None
        return result


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 0.5,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
):
    """Exponential-backoff retry decorator. Raises the last exception."""

    def decorator(fn: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            attempt = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except exceptions as exc:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(
                            "%s failed after %d attempts: %s",
                            fn.__name__,
                            attempt,
                            exc,
                        )
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(
                        "%s failed (attempt %d/%d): %s. Retrying in %.1fs",
                        fn.__name__,
                        attempt,
                        max_attempts,
                        exc,
                        delay,
                    )
                    time.sleep(delay)

        return wrapper

    return decorator


# Module-level breakers per external dependency
stripe_breaker = CircuitBreaker(name="stripe", failure_threshold=5, reset_seconds=30)
assemblyai_breaker = CircuitBreaker(
    name="assemblyai", failure_threshold=3, reset_seconds=60
)
http_breaker = CircuitBreaker(name="http", failure_threshold=10, reset_seconds=15)
