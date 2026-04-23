from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime, UTC
import uuid


class CircleDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CircleMemberDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    circle_id: str = Field(index=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CommunityGroupDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    creator_id: str = Field(index=True)
    name: str
    description: Optional[str] = None
    rules: Optional[str] = None
    member_count: int = Field(default=0)
    is_public: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CommunityMemberDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    group_id: str = Field(index=True)
    user_id: str = Field(index=True)
    role: str = Field(default="member", index=True)
    joined_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DiscussionPostDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    group_id: str = Field(index=True)
    user_id: str = Field(index=True)
    content: str
    parent_id: Optional[str] = Field(default=None, index=True)
    likes_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EventDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    creator_id: str = Field(index=True)
    group_id: Optional[str] = Field(default=None, index=True)
    title: str
    description: Optional[str] = None
    event_type: str = Field(index=True)
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    max_attendees: Optional[int] = None
    attendee_count: int = Field(default=0)
    status: str = Field(default="upcoming", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EventAttendeeDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    event_id: str = Field(index=True)
    user_id: str = Field(index=True)
    rsvp_status: str = Field(default="going", index=True)
    registered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DuetDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    original_video_id: str = Field(index=True)
    response_video_id: str = Field(index=True)
    creator_id: str = Field(index=True)
    duet_type: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CollaborativeVideoDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    video_id: str = Field(index=True)
    creator_id: Optional[str] = Field(default=None, index=True)
    status: str = Field(default="draft", index=True)
    max_participants: int = Field(default=4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class VideoCollaboratorDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    collaborative_video_id: str = Field(index=True)
    user_id: str = Field(index=True)
    role: str = Field(default="participant", index=True)
    joined_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class LiveStreamDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    creator_id: str = Field(index=True)
    title: str
    description: Optional[str] = None
    status: str = Field(default="scheduled", index=True)
    viewer_count: int = Field(default=0)
    peak_viewers: int = Field(default=0)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    recording_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class LiveStreamGuestDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    stream_id: str = Field(index=True)
    user_id: str = Field(index=True)
    status: str = Field(default="invited", index=True)
    joined_at: Optional[datetime] = None


class WatchPartyDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    host_id: str = Field(index=True)
    video_id: str = Field(index=True)
    title: str
    status: str = Field(default="waiting", index=True)
    participant_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class WatchPartyParticipantDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    party_id: str = Field(index=True)
    user_id: str = Field(index=True)
    joined_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PollDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    video_id: str = Field(index=True)
    creator_id: str = Field(index=True)
    question: str
    poll_type: str = Field(index=True)
    correct_answer: Optional[str] = None
    start_time: float
    end_time: float
    total_votes: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PollOptionDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    poll_id: str = Field(index=True)
    text: str
    position: int = Field(default=0)
    vote_count: int = Field(default=0)
    is_correct: bool = Field(default=False)


class PollVoteDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    poll_id: str = Field(index=True)
    option_id: str = Field(index=True)
    user_id: str = Field(index=True)
    voted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ChapterMarkerDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    video_id: str = Field(index=True)
    title: str
    start_time: float
    end_time: float
    thumbnail_url: Optional[str] = None
    creator_id: str = Field(default="")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProductTagDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    video_id: str = Field(index=True)
    creator_id: str = Field(index=True)
    product_name: str
    product_url: str
    product_image_url: Optional[str] = None
    price: float
    currency: str = Field(default="USD")
    position_x: float
    position_y: float
    start_time: float
    end_time: float
    click_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class VideoLinkDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    video_id: str = Field(index=True)
    creator_id: str = Field(index=True)
    title: str
    url: str
    icon: Optional[str] = None
    position: int = Field(default=0)
    click_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PlaylistDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    creator_id: str = Field(index=True)
    title: str
    description: Optional[str] = None
    is_collaborative: bool = Field(default=False)
    is_public: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PlaylistItemDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    playlist_id: str = Field(index=True)
    video_id: str = Field(index=True)
    position: int
    added_by: str = Field(index=True)
    added_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PlaylistCollaboratorDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    playlist_id: str = Field(index=True)
    user_id: str = Field(index=True)
    added_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ChallengeDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    hashtag_id: str = Field(index=True)
    creator_id: str = Field(index=True)
    title: str
    description: Optional[str] = None
    rules: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    prize_description: Optional[str] = None
    status: str = Field(default="upcoming", index=True)
    participant_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ChallengeParticipantDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    challenge_id: str = Field(index=True)
    user_id: str = Field(index=True)
    video_id: str = Field(index=True)
    joined_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DirectMessageDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    sender_id: str = Field(index=True)
    receiver_id: str = Field(index=True)
    conversation_id: Optional[str] = Field(default=None, index=True)
    content: str
    is_encrypted: bool = Field(default=True)
    read_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ConversationDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    participant_1_id: str = Field(index=True)
    participant_2_id: str = Field(index=True)
    last_message_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class BadgeDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    badge_type: str = Field(index=True)
    requirement_type: Optional[str] = None
    requirement_value: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class UserBadgeDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    badge_id: str = Field(index=True)
    earned_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
