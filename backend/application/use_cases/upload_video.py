import uuid
from datetime import datetime, UTC
from typing import BinaryIO, Optional

from ...domain.entities.content_moderation import (
    ContentModeration,
    ModerationReason,
    ModerationSeverity,
    ModerationStatus,
    ModerationType,
)
from ...domain.entities.video import Video, VideoStatus
from ...domain.ports.audit_log_port import AuditEvent, AuditLogPort
from ...domain.ports.queue_port import VideoQueuePort
from ...domain.ports.repository_ports import (
    ContentModerationRepositoryPort,
    HashtagRepositoryPort,
    VideoRepositoryPort,
)
from ...domain.ports.storage_port import StoragePort
from ...domain.ports.text_moderation_port import TextModerationPort
from ..dtos.video_dto import VideoCreateDTO, VideoResponseDTO
from ..services.hashtag_service import HashtagService

# OpenAI category names that are auto-rejection severity.
_AUTO_REJECT_CATEGORIES = {
    "sexual/minors",
    "child_sexual_abuse_material",
    "violence/graphic",
    "self-harm/instructions",
    "hate/threatening",
}


class UploadVideoUseCase:
    def __init__(
        self,
        video_repo: VideoRepositoryPort,
        storage_adapter: StoragePort,
        hashtag_repo: HashtagRepositoryPort,
        video_queue: VideoQueuePort,
        text_moderator: Optional[TextModerationPort] = None,
        moderation_repo: Optional[ContentModerationRepositoryPort] = None,
        audit_log: Optional[AuditLogPort] = None,
    ):
        self._video_repo = video_repo
        self._storage_adapter = storage_adapter
        self._hashtag_repo = hashtag_repo
        self._hashtag_service = HashtagService(hashtag_repo)
        self._video_queue = video_queue
        self._text_moderator = text_moderator
        self._moderation_repo = moderation_repo
        self._audit_log = audit_log

    def execute(
        self, dto: VideoCreateDTO, file_data: BinaryIO, filename: str
    ) -> VideoResponseDTO:
        unique_filename = f"{uuid.uuid4()}_{filename}"
        uploaded_file_path = self._storage_adapter.save(unique_filename, file_data)

        # Pre-screen text content. Apple Guideline 1.2 + spirit of architecture
        # rule "AI output that mutates state must be validated against an
        # explicit schema first" (here: ModerationVerdict).
        verdict = None
        initial_status = VideoStatus.UPLOADING
        if self._text_moderator is not None:
            try:
                text = f"{dto.title}\n\n{dto.description or ''}"
                verdict = self._text_moderator.classify(text)
                if verdict.flagged and any(
                    cat in _AUTO_REJECT_CATEGORIES for cat in verdict.reasons
                ):
                    initial_status = VideoStatus.REJECTED
                elif verdict.flagged:
                    # Soft flag: enqueue but mark for human review later.
                    initial_status = VideoStatus.UPLOADING

            except Exception:
                # Fail open — never block uploads on moderation outage.
                verdict = None

        video = Video(
            title=dto.title,
            description=dto.description,
            creator_id=dto.creator_id,
            status=initial_status,
        )

        saved_video = self._video_repo.save(video)

        # Persist a moderation record for any flagged upload.
        if verdict and verdict.flagged and self._moderation_repo is not None:
            severity = (
                ModerationSeverity.CRITICAL
                if initial_status == VideoStatus.REJECTED
                else ModerationSeverity.MEDIUM
            )
            record = ContentModeration(
                content_type="video",
                content_id=saved_video.id,
                user_id=saved_video.creator_id,
                status=(
                    ModerationStatus.REJECTED
                    if initial_status == VideoStatus.REJECTED
                    else ModerationStatus.FLAGGED
                ),
                moderation_type=ModerationType.AUTOMATIC,
                severity=severity,
                reason=ModerationReason.INAPPROPRIATE_CONTENT,
                confidence_score=verdict.score,
                ai_labels={"reasons": list(verdict.reasons)},
                auto_action="reject" if initial_status == VideoStatus.REJECTED else "flag",
            )
            self._moderation_repo.save(record)

            if self._audit_log is not None:
                self._audit_log.append(
                    AuditEvent(
                        actor_id=saved_video.creator_id,
                        action=f"video_auto_{record.auto_action}ed",
                        target_type="video",
                        target_id=saved_video.id,
                        before_hash=None,
                        after_hash=None,
                        occurred_at=datetime.now(UTC),
                    )
                )

        self._hashtag_service.process_video_hashtags(
            saved_video.id, dto.title, dto.description
        )

        # Don't waste compute transcoding rejected uploads.
        if initial_status != VideoStatus.REJECTED:
            self._video_queue.enqueue_video_processing(saved_video.id)

        return VideoResponseDTO(
            id=saved_video.id,
            title=saved_video.title,
            description=saved_video.description,
            creator_id=saved_video.creator_id,
            status=saved_video.status,
            url=None,
            thumbnail_url=None,
            views=saved_video.views,
            likes=saved_video.likes,
            duration=saved_video.duration,
        )
