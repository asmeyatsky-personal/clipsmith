"""Execute a pending GDPR deletion request synchronously.

GDPR Art. 17 (Right to Erasure) — once a user submits a deletion request,
we must complete it within 30 days. We do it inline at request time
because the user is being logged out anyway.
"""
from datetime import datetime, UTC
from typing import Iterable

from ...domain.ports.audit_log_port import AuditEvent, AuditLogPort

# All deletable categories. Ordered so child rows go before parents.
_ALL_CATEGORIES = (
    "tips",
    "messages",
    "comments",
    "likes",
    "follows",
    "videos",
    "notifications",
    "analytics",
    "preferences",
)


class ProcessGDPRDeletionUseCase:
    """Executes a deletion request against the compliance repo.

    The compliance_repo here is the legacy SQLiteComplianceRepository — it's
    been kept in infrastructure but exposes a stable surface for this use
    case. We don't depend on a domain port for it because the operations are
    inherently database-wide cascades; a richer port would just be a
    typing alias.
    """

    def __init__(self, compliance_repo, audit_log: AuditLogPort):
        self._repo = compliance_repo
        self._audit = audit_log

    def execute(
        self,
        user_id: str,
        request_id: str,
        categories: Iterable[str],
    ) -> dict:
        cats = list(categories) or list(_ALL_CATEGORIES)
        if "all" in cats:
            cats = list(_ALL_CATEGORIES)

        deleted: list[str] = []
        for cat in cats:
            try:
                self._repo.delete_user_data_category(user_id, cat)
                deleted.append(cat)
            except Exception as e:
                # Best-effort — continue deleting other categories.
                self._audit.append(
                    AuditEvent(
                        actor_id=user_id,
                        action="gdpr_delete_category_failed",
                        target_type="user_data_category",
                        target_id=cat,
                        before_hash=None,
                        after_hash=str(e)[:64],
                        occurred_at=datetime.now(UTC),
                        correlation_id=request_id,
                    )
                )

        # Mark the request completed
        self._repo.update_gdpr_request_status(
            request_id, status="completed", completed_at=datetime.now(UTC)
        )

        self._audit.append(
            AuditEvent(
                actor_id=user_id,
                action="gdpr_delete_executed",
                target_type="user",
                target_id=user_id,
                before_hash=None,
                after_hash=",".join(deleted),
                occurred_at=datetime.now(UTC),
                correlation_id=request_id,
            )
        )
        return {"deleted_categories": deleted, "request_id": request_id}
