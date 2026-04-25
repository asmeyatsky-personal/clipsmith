"""User-initiated content report use case.

Apple App Store Guideline 1.2 requires UGC apps to provide a way for users
to report objectionable content with response within 24 hours.
"""
from datetime import datetime, UTC

from ...domain.entities.content_moderation import (
    ContentModeration,
    ModerationReason,
    ModerationSeverity,
    ModerationStatus,
    ModerationType,
)
from ...domain.ports.audit_log_port import AuditEvent, AuditLogPort
from ...domain.ports.repository_ports import ContentModerationRepositoryPort

# Mapping from user-supplied reason text to ModerationReason enum.
_REASON_MAP = {
    "spam": ModerationReason.SPAM,
    "harmful": ModerationReason.INAPPROPRIATE_CONTENT,
    "inappropriate": ModerationReason.INAPPROPRIATE_CONTENT,
    "violence": ModerationReason.VIOLENCE,
    "harassment": ModerationReason.HARASSMENT,
    "hate": ModerationReason.HATE_SPEECH,
    "copyright": ModerationReason.COPYRIGHT_VIOLATION,
    "self_harm": ModerationReason.SELF_HARM,
    "misinformation": ModerationReason.MISINFORMATION,
}


class ReportContentUseCase:
    def __init__(
        self,
        moderation_repo: ContentModerationRepositoryPort,
        audit_log: AuditLogPort,
    ):
        self._repo = moderation_repo
        self._audit = audit_log

    def execute(
        self,
        *,
        content_type: str,
        content_id: str,
        reporter_id: str,
        reason_text: str,
        creator_id: str | None = None,
    ) -> ContentModeration:
        normalized = (reason_text or "").strip().lower()
        reason = _REASON_MAP.get(normalized, ModerationReason.COMMUNITY_GUIDELINE_VIOLATION)

        record = ContentModeration(
            content_type=content_type,
            content_id=content_id,
            user_id=creator_id,
            reporter_id=reporter_id,
            status=ModerationStatus.PENDING,
            moderation_type=ModerationType.USER_REPORT,
            severity=ModerationSeverity.MEDIUM,
            reason=reason,
        )
        saved = self._repo.save(record)

        self._audit.append(
            AuditEvent(
                actor_id=reporter_id,
                action="content_reported",
                target_type=content_type,
                target_id=content_id,
                before_hash=None,
                after_hash=saved.id,
                occurred_at=datetime.now(UTC),
                correlation_id=None,
            )
        )
        return saved
