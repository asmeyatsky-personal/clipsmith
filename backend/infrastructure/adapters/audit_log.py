"""Audit log adapter — append-only persistence + structured log mirror.

Architectural Rules §4: every write emits an audit event.

For now we emit to:
  1. A dedicated `audit_log` SQLModel table (append-only by convention)
  2. structlog/print as a redundant trail (structlog wired in observability phase)

Future: split IAM so the audit log table has a separate writer role.
"""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime
from typing import Any

from sqlmodel import Field, Session, SQLModel

from backend.domain.ports.audit_log_port import AuditEvent, AuditLogPort

logger = logging.getLogger("audit")


class AuditLogDB(SQLModel, table=True):
    __tablename__ = "audit_log"
    id: int | None = Field(default=None, primary_key=True)
    actor_id: str | None = Field(default=None, index=True)
    action: str = Field(index=True)
    target_type: str = Field(index=True)
    target_id: str | None = Field(default=None, index=True)
    before_hash: str | None = None
    after_hash: str | None = None
    occurred_at: datetime = Field(index=True)
    correlation_id: str | None = Field(default=None, index=True)


def hash_state(payload: Any) -> str:
    """Stable SHA-256 hash of a JSON-serializable state snapshot."""
    if payload is None:
        return ""
    if hasattr(payload, "__dict__"):
        payload = {
            k: v
            for k, v in vars(payload).items()
            if not k.startswith("_")
        }
    raw = json.dumps(payload, default=str, sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()[:32]


class SQLModelAuditLog(AuditLogPort):
    def __init__(self, session: Session):
        self._session = session

    def append(self, event: AuditEvent) -> None:
        row = AuditLogDB(
            actor_id=event.actor_id,
            action=event.action,
            target_type=event.target_type,
            target_id=event.target_id,
            before_hash=event.before_hash,
            after_hash=event.after_hash,
            occurred_at=event.occurred_at,
            correlation_id=event.correlation_id,
        )
        self._session.add(row)
        self._session.commit()
        logger.info(
            "audit",
            extra={
                "actor": event.actor_id,
                "action": event.action,
                "target_type": event.target_type,
                "target_id": event.target_id,
                "after_hash": event.after_hash,
            },
        )


class NoopAuditLog(AuditLogPort):
    """For tests where audit is irrelevant."""

    def append(self, event: AuditEvent) -> None:
        return None
