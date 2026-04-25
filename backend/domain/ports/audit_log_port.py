"""Append-only audit log port. Per Architectural Rules §4."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, kw_only=True)
class AuditEvent:
    actor_id: str | None
    action: str
    target_type: str
    target_id: str | None
    before_hash: str | None
    after_hash: str | None
    occurred_at: datetime
    correlation_id: str | None = None


class AuditLogPort(ABC):
    @abstractmethod
    def append(self, event: AuditEvent) -> None: ...
