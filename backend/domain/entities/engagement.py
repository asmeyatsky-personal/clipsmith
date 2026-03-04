from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass(frozen=True, kw_only=True)
class Poll:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    video_id: str
    creator_id: str
    question: str
    poll_type: str = "multiple_choice"  # multiple_choice, quiz, rating
    correct_answer: Optional[str] = None  # For quiz-type polls
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_votes: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class PollOption:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    poll_id: str
    text: str
    vote_count: int = 0
    is_correct: bool = False


@dataclass(frozen=True, kw_only=True)
class PollVote:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    poll_id: str
    option_id: str
    user_id: str
    voted_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class ChapterMarker:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    video_id: str
    title: str
    start_time: float  # In seconds
    end_time: float  # In seconds
    thumbnail_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class ProductTag:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    video_id: str
    creator_id: str
    product_name: str
    product_url: str
    product_image_url: Optional[str] = None
    price: float = 0.0
    currency: str = "USD"
    position_x: float = 0.0
    position_y: float = 0.0
    start_time: float = 0.0  # In seconds
    end_time: float = 0.0  # In seconds
    click_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class VideoLink:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    video_id: str
    creator_id: str
    title: str
    url: str
    icon: Optional[str] = None
    position: int = 0
    click_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class Challenge:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hashtag_id: str
    creator_id: str
    title: str
    description: str = ""
    rules: str = ""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    prize_description: Optional[str] = None
    status: str = "draft"  # draft, active, ended, cancelled
    participant_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class ChallengeParticipant:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    challenge_id: str
    user_id: str
    video_id: str
    joined_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class Badge:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    icon_url: Optional[str] = None
    badge_type: str = "achievement"  # achievement, milestone, special
    requirement_type: str = ""  # followers, views, uploads, streak
    requirement_value: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class UserBadge:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    badge_id: str
    earned_at: datetime = field(default_factory=datetime.utcnow)
