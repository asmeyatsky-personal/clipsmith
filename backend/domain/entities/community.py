from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Optional
import uuid


@dataclass(frozen=True, kw_only=True)
class Circle:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Owner of the circle
    name: str
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class CircleMember:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    circle_id: str
    member_id: str
    added_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class CommunityGroup:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str
    name: str
    description: str = ""
    rules: str = ""
    member_count: int = 0
    is_public: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class CommunityMember:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    user_id: str
    role: str = "member"  # member, moderator, admin
    joined_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class DiscussionPost:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    user_id: str
    content: str
    parent_id: Optional[str] = None  # For threaded replies
    likes_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class Event:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str
    group_id: Optional[str] = None
    title: str
    description: str = ""
    event_type: str = "meetup"  # meetup, workshop, livestream, contest
    start_time: datetime
    end_time: datetime
    location: str = ""
    max_attendees: int = 0
    attendee_count: int = 0
    status: str = "scheduled"  # scheduled, active, completed, cancelled
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class EventAttendee:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str
    user_id: str
    rsvp_status: str = "going"  # going, interested, not_going
    registered_at: datetime = field(default_factory=datetime.utcnow)
