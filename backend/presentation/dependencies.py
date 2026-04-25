"""Composition root for FastAPI dependency injection.

This module is exempt from the presentation→infrastructure import contract
in import-linter. It wires concrete adapters to ports for use cases.
All other presentation modules MUST import from here, never directly from
infrastructure.
"""
from fastapi import Depends, Request
from sqlmodel import Session

from ..application.services.two_factor_service import TwoFactorService
from ..application.use_cases.authenticate_user import AuthenticateUserUseCase
from ..application.use_cases.manage_2fa import (
    DisableTwoFactorUseCase,
    GetTwoFactorStatusUseCase,
    SetupTwoFactorUseCase,
    VerifyLoginTwoFactorUseCase,
    VerifyTwoFactorSetupUseCase,
)
from ..application.use_cases.password_reset import (
    ConfirmPasswordResetUseCase,
    RequestPasswordResetUseCase,
)
from ..application.use_cases.block_user import BlockUserUseCase, UnblockUserUseCase
from ..application.use_cases.report_content import ReportContentUseCase
from ..application.use_cases.register_user import RegisterUserUseCase
from ..application.use_cases.upload_video import UploadVideoUseCase
from ..domain.ports.auth_security_port import (
    PasswordResetRepositoryPort,
    TwoFactorRepositoryPort,
)
from ..domain.ports.email_port import EmailSenderPort
from ..domain.ports.queue_port import VideoQueuePort
from ..domain.ports.repository_ports import (
    ContentModerationRepositoryPort,
    FollowRepositoryPort,
    HashtagRepositoryPort,
    InteractionRepositoryPort,
    NotificationRepositoryPort,
    UserRepositoryPort,
    VideoRepositoryPort,
)
from ..domain.ports.analytics_repository_port import AnalyticsRepositoryPort
from ..domain.ports.audit_log_port import AuditLogPort
from ..domain.ports.payment_repository_port import PaymentRepositoryPort
from ..domain.ports.security_port import JWTPort, PasswordHelperPort
from ..domain.ports.storage_port import StoragePort
from ..domain.ports.push_port import DeviceTokenRepositoryPort, PushSenderPort
from ..domain.ports.user_block_port import UserBlockRepositoryPort
from ..infrastructure.adapters.apns_push_adapter import get_push_sender
from ..infrastructure.adapters.audit_log import SQLModelAuditLog
from ..infrastructure.adapters.email_adapter import get_email_adapter
from ..infrastructure.adapters.storage_factory import get_storage_adapter
# Legacy re-exports for routers that haven't yet been thinned to use cases.
# These come through the composition root (this module) so the import-linter
# contract is preserved; the goal is to eliminate them as each router ships
# with proper use cases.
from ..infrastructure.repositories import models as db_models  # noqa: F401
from ..infrastructure.repositories.database import get_session as _raw_get_session
from ..infrastructure.repositories.sqlite_caption_repo import SQLiteCaptionRepository
from ..infrastructure.repositories.sqlite_community_repo import SQLiteCommunityRepository
from ..infrastructure.repositories.sqlite_compliance_repo import SQLiteComplianceRepository
from ..infrastructure.repositories.sqlite_course_repo import SQLiteCourseRepository
from ..infrastructure.repositories.sqlite_discovery_repo import SQLiteDiscoveryRepository
from ..infrastructure.repositories.sqlite_engagement_repo import SQLiteEngagementRepository
from ..infrastructure.repositories.sqlite_social_repo import SQLiteSocialRepository
from ..infrastructure.repositories.sqlite_tip_repo import SQLiteTipRepository
from ..infrastructure.repositories.sqlite_video_editor_repo import (
    SQLiteVideoEditorRepository,
)
from ..infrastructure.queue import get_video_queue as _raw_get_video_queue
from ..infrastructure.queue.tasks import (
    generate_captions_task as _raw_generate_captions_task,
    process_video_task as _raw_process_video_task,
)
from ..infrastructure.queue.video_queue_adapter import RQVideoQueueAdapter
from ..infrastructure.repositories.database import get_session
from ..infrastructure.repositories.sqlite_auth_security_repo import (
    SQLitePasswordResetRepository,
    SQLiteTwoFactorRepository,
)
from ..infrastructure.repositories.sqlite_analytics_repo import (
    SQLiteAnalyticsRepository,
)
from ..infrastructure.repositories.sqlite_content_moderation_repo import (
    SQLiteContentModerationRepository,
)
from ..infrastructure.repositories.sqlite_follow_repo import SQLiteFollowRepository
from ..infrastructure.repositories.sqlite_hashtag_repo import SQLiteHashtagRepository
from ..infrastructure.repositories.sqlite_interaction_repo import (
    SQLiteInteractionRepository,
)
from ..infrastructure.repositories.sqlite_notification_repo import (
    SQLiteNotificationRepository,
)
from ..infrastructure.repositories.sqlite_payment_repo import SQLitePaymentRepository
from ..infrastructure.repositories.sqlite_device_token_repo import (
    SQLiteDeviceTokenRepository,
)
from ..infrastructure.repositories.sqlite_user_block_repo import (
    SQLiteUserBlockRepository,
)
from ..infrastructure.repositories.sqlite_user_repo import SQLiteUserRepository
from ..infrastructure.repositories.sqlite_video_repo import SQLiteVideoRepository
from ..infrastructure.security.jwt_adapter import JWTAdapter
from ..infrastructure.security.security_adapter import PasswordHelper


# --- Repository providers ---


def get_user_repo(session: Session = Depends(get_session)) -> UserRepositoryPort:
    return SQLiteUserRepository(session)


def get_video_repo(session: Session = Depends(get_session)) -> VideoRepositoryPort:
    return SQLiteVideoRepository(session)


def get_hashtag_repo(session: Session = Depends(get_session)) -> HashtagRepositoryPort:
    return SQLiteHashtagRepository(session)


def get_interaction_repo(
    session: Session = Depends(get_session),
) -> InteractionRepositoryPort:
    return SQLiteInteractionRepository(session)


def get_follow_repo(
    session: Session = Depends(get_session),
) -> FollowRepositoryPort:
    return SQLiteFollowRepository(session)


def get_notification_repo(
    session: Session = Depends(get_session),
) -> NotificationRepositoryPort:
    return SQLiteNotificationRepository(session)


def get_analytics_repo(
    session: Session = Depends(get_session),
) -> AnalyticsRepositoryPort:
    return SQLiteAnalyticsRepository(session)


def get_content_moderation_repo(
    session: Session = Depends(get_session),
) -> ContentModerationRepositoryPort:
    return SQLiteContentModerationRepository(session)


def get_payment_repo(
    session: Session = Depends(get_session),
) -> PaymentRepositoryPort:
    return SQLitePaymentRepository(session)


def get_audit_log(session: Session = Depends(get_session)) -> AuditLogPort:
    return SQLModelAuditLog(session)


def get_report_content_use_case(
    moderation_repo: ContentModerationRepositoryPort = Depends(get_content_moderation_repo),
    audit: AuditLogPort = Depends(get_audit_log),
) -> ReportContentUseCase:
    return ReportContentUseCase(moderation_repo, audit)


def get_user_block_repo(
    session: Session = Depends(get_session),
) -> UserBlockRepositoryPort:
    return SQLiteUserBlockRepository(session)


def get_block_user_use_case(
    repo: UserBlockRepositoryPort = Depends(get_user_block_repo),
    audit: AuditLogPort = Depends(get_audit_log),
) -> BlockUserUseCase:
    return BlockUserUseCase(repo, audit)


def get_unblock_user_use_case(
    repo: UserBlockRepositoryPort = Depends(get_user_block_repo),
    audit: AuditLogPort = Depends(get_audit_log),
) -> UnblockUserUseCase:
    return UnblockUserUseCase(repo, audit)


def get_device_token_repo(
    session: Session = Depends(get_session),
) -> DeviceTokenRepositoryPort:
    return SQLiteDeviceTokenRepository(session)


def get_push_sender_dep() -> PushSenderPort:
    return get_push_sender()


# --- Legacy router providers (transitional) ---


def get_session_for_router(session: Session = Depends(get_session)) -> Session:
    """Re-export of the SQLModel session for routers with inline queries.
    Use sparingly — prefer specific repos. Each call site should migrate to
    a use case + repo method as the corresponding feature ships.
    """
    return session


def get_caption_repo(session: Session = Depends(get_session)):
    return SQLiteCaptionRepository(session)


def get_tip_repo(session: Session = Depends(get_session)):
    return SQLiteTipRepository(session)


def get_community_repo(session: Session = Depends(get_session)):
    return SQLiteCommunityRepository(session)


def get_compliance_repo(session: Session = Depends(get_session)):
    return SQLiteComplianceRepository(session)


def get_course_repo(session: Session = Depends(get_session)):
    return SQLiteCourseRepository(session)


def get_discovery_repo(session: Session = Depends(get_session)):
    return SQLiteDiscoveryRepository(session)


def get_engagement_repo(session: Session = Depends(get_session)):
    return SQLiteEngagementRepository(session)


def get_social_repo(session: Session = Depends(get_session)):
    return SQLiteSocialRepository(session)


def get_video_editor_repo(session: Session = Depends(get_session)):
    return SQLiteVideoEditorRepository(session)


def get_video_processing_queue():
    """Returns the RQ video processing queue. Use for direct .enqueue() calls
    until upload/captions paths are routed through VideoQueuePort."""
    return _raw_get_video_queue()


# Re-exported for routers that still need direct task references.
generate_captions_task = _raw_generate_captions_task
process_video_task = _raw_process_video_task

# Legacy class re-exports for routers with inline `SQLiteXRepo(session)` /
# `JWTAdapter.verify_token(...)` calls. To be removed as routers move to
# proper port injection.
from ..infrastructure.repositories.sqlite_caption_repo import (  # noqa: E402, F401
    SQLiteCaptionRepository,
)
from ..infrastructure.repositories.sqlite_hashtag_repo import (  # noqa: E402, F401
    SQLiteHashtagRepository,
)
from ..infrastructure.repositories.sqlite_interaction_repo import (  # noqa: E402, F401
    SQLiteInteractionRepository,
)
from ..infrastructure.repositories.sqlite_payment_repo import (  # noqa: E402, F401
    SQLitePaymentRepository,
)
from ..infrastructure.repositories.sqlite_tip_repo import (  # noqa: E402, F401
    SQLiteTipRepository,
)
from ..infrastructure.repositories.sqlite_user_repo import (  # noqa: E402, F401
    SQLiteUserRepository,
)
from ..infrastructure.repositories.sqlite_video_editor_repo import (  # noqa: E402, F401
    SQLiteVideoEditorRepository,
)
from ..infrastructure.repositories.sqlite_video_repo import (  # noqa: E402, F401
    SQLiteVideoRepository,
)
from ..infrastructure.security.jwt_adapter import JWTAdapter  # noqa: E402, F401
from ..infrastructure.security.security_adapter import (  # noqa: E402, F401
    SecurityAdapter,
)


# --- Adapter / port providers ---


def get_password_helper() -> PasswordHelperPort:
    return PasswordHelper()


def get_jwt() -> JWTPort:
    return JWTAdapter()


def get_storage() -> StoragePort:
    return get_storage_adapter()


def get_email_service() -> EmailSenderPort:
    return get_email_adapter()


def get_password_reset_repo(
    session: Session = Depends(get_session),
) -> PasswordResetRepositoryPort:
    return SQLitePasswordResetRepository(session)


def get_two_factor_repo(
    session: Session = Depends(get_session),
) -> TwoFactorRepositoryPort:
    return SQLiteTwoFactorRepository(session)


def get_two_factor_service() -> TwoFactorService:
    return TwoFactorService(user_repo=None)


def get_video_queue(
    storage: StoragePort = Depends(get_storage),
) -> VideoQueuePort:
    return RQVideoQueueAdapter(file_path_resolver=lambda vid: str(vid))


# --- Use case providers ---


def get_register_use_case(
    user_repo: UserRepositoryPort = Depends(get_user_repo),
    password: PasswordHelperPort = Depends(get_password_helper),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(user_repo, password)


def get_authenticate_use_case(
    user_repo: UserRepositoryPort = Depends(get_user_repo),
    password: PasswordHelperPort = Depends(get_password_helper),
    jwt: JWTPort = Depends(get_jwt),
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(user_repo, password, jwt)


def get_upload_video_use_case(
    video_repo: VideoRepositoryPort = Depends(get_video_repo),
    storage: StoragePort = Depends(get_storage),
    hashtag_repo: HashtagRepositoryPort = Depends(get_hashtag_repo),
    queue: VideoQueuePort = Depends(get_video_queue),
) -> UploadVideoUseCase:
    return UploadVideoUseCase(video_repo, storage, hashtag_repo, queue)


def get_request_password_reset_use_case(
    user_repo: UserRepositoryPort = Depends(get_user_repo),
    reset_repo: PasswordResetRepositoryPort = Depends(get_password_reset_repo),
    email: EmailSenderPort = Depends(get_email_service),
) -> RequestPasswordResetUseCase:
    return RequestPasswordResetUseCase(user_repo, reset_repo, email)


def get_confirm_password_reset_use_case(
    user_repo: UserRepositoryPort = Depends(get_user_repo),
    reset_repo: PasswordResetRepositoryPort = Depends(get_password_reset_repo),
    password: PasswordHelperPort = Depends(get_password_helper),
) -> ConfirmPasswordResetUseCase:
    return ConfirmPasswordResetUseCase(user_repo, reset_repo, password)


def get_2fa_status_use_case(
    repo: TwoFactorRepositoryPort = Depends(get_two_factor_repo),
) -> GetTwoFactorStatusUseCase:
    return GetTwoFactorStatusUseCase(repo)


def get_2fa_setup_use_case(
    repo: TwoFactorRepositoryPort = Depends(get_two_factor_repo),
    service: TwoFactorService = Depends(get_two_factor_service),
) -> SetupTwoFactorUseCase:
    return SetupTwoFactorUseCase(repo, service)


def get_2fa_verify_use_case(
    repo: TwoFactorRepositoryPort = Depends(get_two_factor_repo),
    service: TwoFactorService = Depends(get_two_factor_service),
) -> VerifyTwoFactorSetupUseCase:
    return VerifyTwoFactorSetupUseCase(repo, service)


def get_2fa_disable_use_case(
    repo: TwoFactorRepositoryPort = Depends(get_two_factor_repo),
    user_repo: UserRepositoryPort = Depends(get_user_repo),
    password: PasswordHelperPort = Depends(get_password_helper),
) -> DisableTwoFactorUseCase:
    return DisableTwoFactorUseCase(repo, user_repo, password)


def get_2fa_login_verify_use_case(
    repo: TwoFactorRepositoryPort = Depends(get_two_factor_repo),
    service: TwoFactorService = Depends(get_two_factor_service),
) -> VerifyLoginTwoFactorUseCase:
    return VerifyLoginTwoFactorUseCase(repo, service)


def get_current_user(
    request: Request,
    user_repo: UserRepositoryPort = Depends(get_user_repo),
    jwt: JWTPort = Depends(get_jwt),
):
    """Resolve the authenticated user from the request cookie or Authorization header."""
    from fastapi import HTTPException, status

    token = request.cookies.get("access_token")
    if not token:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user
