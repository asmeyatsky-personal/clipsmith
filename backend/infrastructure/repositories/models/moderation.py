from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime, UTC
import uuid


class ContentModerationDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    content_type: str = Field(index=True)
    content_id: str = Field(index=True)
    user_id: Optional[str] = Field(default=None, index=True)
    reporter_id: Optional[str] = Field(default=None, index=True)
    status: str = Field(default="pending", index=True)
    moderation_type: str = Field(default="automatic", index=True)
    severity: str = Field(default="low", index=True)
    reason: Optional[str] = None
    confidence_score: Optional[float] = None
    ai_labels: Optional[str] = None
    human_reviewer_id: Optional[str] = Field(default=None, index=True)
    human_notes: Optional[str] = None
    auto_action: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    reviewed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class GDPRRequestDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    request_type: str = Field(index=True)
    status: str = Field(default="pending", index=True)
    details: Optional[str] = None
    result_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: Optional[datetime] = None


class ConsentRecordDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    consent_type: str = Field(index=True)
    granted: bool = Field(default=False)
    ip_address: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AgeVerificationDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    date_of_birth: str
    verification_method: str = Field(default="self_declared")
    verified: bool = Field(default=False)
    verified_age: Optional[int] = None
    is_minor: bool = Field(default=False)
    requires_parental_consent: bool = Field(default=False)
    status: str = Field(default="pending", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
