from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from typing import Optional, List
import uuid


@dataclass(frozen=True, kw_only=True)
class Playlist:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str
    title: str
    description: str = ""
    is_collaborative: bool = False
    is_public: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def add_item(self, video_id: str, position: int, added_by: str) -> "PlaylistItem":
        """Create a new playlist item for this playlist."""
        return PlaylistItem(
            playlist_id=self.id,
            video_id=video_id,
            position=position,
            added_by=added_by,
        )

    def remove_item(self, item_id: str) -> "Playlist":
        """Return playlist unchanged; actual removal handled by repository."""
        return self


@dataclass(frozen=True, kw_only=True)
class PlaylistItem:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    playlist_id: str
    video_id: str
    position: int = 0
    added_by: str = ""
    added_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, kw_only=True)
class PlaylistCollaborator:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    playlist_id: str
    user_id: str
    added_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, kw_only=True)
class UserPreferences:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    interest_weight: float = 0.4
    community_weight: float = 0.3
    virality_weight: float = 0.2
    freshness_weight: float = 0.1
    preferred_categories: List[str] = field(default_factory=list)
    preferred_languages: List[str] = field(default_factory=list)
    location: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None


@dataclass(frozen=True, kw_only=True)
class FavoriteCreator:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    creator_id: str
    priority_notifications: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, kw_only=True)
class DiscoveryScore:
    video_id: str
    interest_score: float = 0.0
    community_score: float = 0.0
    virality_score: float = 0.0
    freshness_score: float = 0.0
    total_score: float = 0.0
    reasons: List[str] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True)
class TrafficSource:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    video_id: str
    source_type: str = ""  # organic, search, share, external, recommended
    referrer_url: Optional[str] = None
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, kw_only=True)
class RetentionData:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    video_id: str
    second_offset: int = 0
    viewer_count: int = 0
    drop_off_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, kw_only=True)
class PostingTimeRecommendation:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    day_of_week: int = 0  # 0=Monday, 6=Sunday
    hour: int = 0  # 0-23
    engagement_score: float = 0.0
    sample_size: int = 0
    updated_at: Optional[datetime] = None
