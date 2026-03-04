from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Optional
import uuid


@dataclass(frozen=True, kw_only=True)
class Duet:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    original_video_id: str
    response_video_id: str
    creator_id: str
    duet_type: str = "duet"  # duet, reaction, stitch
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class CollaborativeVideo:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    video_id: str
    status: str = "open"  # open, in_progress, completed, cancelled
    max_participants: int = 4
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class VideoCollaborator:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    collaborative_video_id: str
    user_id: str
    role: str = "contributor"  # contributor, editor, reviewer
    joined_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class LiveStream:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str
    title: str
    description: str = ""
    status: str = "scheduled"  # scheduled, live, ended, cancelled
    viewer_count: int = 0
    peak_viewers: int = 0
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    recording_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def go_live(self) -> "LiveStream":
        """Transition stream to live status."""
        return replace(
            self,
            status="live",
            started_at=datetime.utcnow(),
        )

    def end_stream(self) -> "LiveStream":
        """End the live stream."""
        return replace(
            self,
            status="ended",
            ended_at=datetime.utcnow(),
        )

    def add_viewer(self) -> "LiveStream":
        """Increment viewer count and update peak if needed."""
        new_count = self.viewer_count + 1
        new_peak = max(self.peak_viewers, new_count)
        return replace(
            self,
            viewer_count=new_count,
            peak_viewers=new_peak,
        )

    def remove_viewer(self) -> "LiveStream":
        """Decrement viewer count."""
        new_count = max(0, self.viewer_count - 1)
        return replace(self, viewer_count=new_count)


@dataclass(frozen=True, kw_only=True)
class LiveStreamGuest:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    stream_id: str
    user_id: str
    status: str = "invited"  # invited, joined, left
    joined_at: Optional[datetime] = None


@dataclass(frozen=True, kw_only=True)
class WatchParty:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    host_id: str
    video_id: str
    title: str
    status: str = "waiting"  # waiting, active, ended
    participant_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def start(self) -> "WatchParty":
        """Start the watch party."""
        return replace(self, status="active")

    def end(self) -> "WatchParty":
        """End the watch party."""
        return replace(self, status="ended")


@dataclass(frozen=True, kw_only=True)
class WatchPartyParticipant:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    party_id: str
    user_id: str
    joined_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class DirectMessage:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    receiver_id: str
    content: str
    is_encrypted: bool = True
    read_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class Conversation:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    participant_1_id: str
    participant_2_id: str
    last_message_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
