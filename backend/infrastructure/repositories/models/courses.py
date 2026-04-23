from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime, UTC
import uuid


class CourseDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    creator_id: str = Field(index=True)
    title: str
    description: Optional[str] = None
    price: float
    currency: str = Field(default="USD")
    category: str = Field(index=True)
    status: str = Field(default="draft", index=True)
    enrollment_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CourseLessonDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    course_id: str = Field(index=True)
    title: str
    description: Optional[str] = None
    video_id: Optional[str] = Field(default=None, index=True)
    position: int
    duration: float = Field(default=0.0)
    is_free_preview: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CourseEnrollmentDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    course_id: str = Field(index=True)
    user_id: str = Field(index=True)
    status: str = Field(default="enrolled", index=True)
    progress_percentage: float = Field(default=0.0)
    enrolled_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: Optional[datetime] = None


class LessonProgressDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    enrollment_id: str = Field(index=True)
    lesson_id: str = Field(index=True)
    user_id: Optional[str] = Field(default=None, index=True)
    completed: bool = Field(default=False)
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class UserPreferencesDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(unique=True, index=True)
    interest_weight: float = Field(default=1.0)
    community_weight: float = Field(default=1.0)
    virality_weight: float = Field(default=1.0)
    freshness_weight: float = Field(default=1.0)
    preferred_categories: Optional[str] = None
    preferred_languages: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None


class FavoriteCreatorDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    creator_id: str = Field(index=True)
    priority_notifications: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
