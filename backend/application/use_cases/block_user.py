"""Block / unblock user use cases. Apple Guideline 1.2."""
from datetime import datetime, UTC

from ...domain.ports.audit_log_port import AuditEvent, AuditLogPort
from ...domain.ports.user_block_port import UserBlockRepositoryPort


class BlockUserUseCase:
    def __init__(
        self,
        repo: UserBlockRepositoryPort,
        audit: AuditLogPort,
    ):
        self._repo = repo
        self._audit = audit

    def execute(self, blocker_id: str, blocked_id: str) -> None:
        if blocker_id == blocked_id:
            raise ValueError("Cannot block yourself")
        self._repo.block(blocker_id, blocked_id)
        self._audit.append(
            AuditEvent(
                actor_id=blocker_id,
                action="user_blocked",
                target_type="user",
                target_id=blocked_id,
                before_hash=None,
                after_hash=None,
                occurred_at=datetime.now(UTC),
            )
        )


class UnblockUserUseCase:
    def __init__(
        self,
        repo: UserBlockRepositoryPort,
        audit: AuditLogPort,
    ):
        self._repo = repo
        self._audit = audit

    def execute(self, blocker_id: str, blocked_id: str) -> None:
        self._repo.unblock(blocker_id, blocked_id)
        self._audit.append(
            AuditEvent(
                actor_id=blocker_id,
                action="user_unblocked",
                target_type="user",
                target_id=blocked_id,
                before_hash=None,
                after_hash=None,
                occurred_at=datetime.now(UTC),
            )
        )
