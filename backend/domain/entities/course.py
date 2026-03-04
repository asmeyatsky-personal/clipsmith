from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Optional, List
import uuid


@dataclass(frozen=True, kw_only=True)
class Course:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str
    title: str
    description: str = ""
    price: float = 0.0
    currency: str = "USD"
    category: str = ""
    status: str = "draft"  # draft, published, archived
    enrollment_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class CourseLesson:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str
    title: str
    description: str = ""
    video_id: Optional[str] = None
    position: int = 0
    duration: float = 0.0  # In seconds
    is_free_preview: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class CourseEnrollment:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str
    user_id: str
    status: str = "active"  # active, completed, cancelled
    progress_percentage: float = 0.0
    enrolled_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


@dataclass(frozen=True, kw_only=True)
class SubscriptionTier:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str
    name: str
    price: float = 0.0
    currency: str = "USD"
    interval: str = "month"  # month, year
    description: str = ""
    benefits: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class CreatorFundEligibility:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    follower_count: int = 0
    monthly_views: int = 0
    is_eligible: bool = False
    applied_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    status: str = "pending"  # pending, approved, rejected

    def check_eligibility(self) -> bool:
        """Check if creator meets fund eligibility requirements.

        Returns True if follower_count >= 1000 and monthly_views >= 10000.
        """
        return self.follower_count >= 1000 and self.monthly_views >= 10000
