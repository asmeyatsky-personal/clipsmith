from typing import Optional, List
from sqlmodel import Field, SQLModel
from datetime import datetime, UTC
import uuid


class VideoProjectDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    title: str
    description: Optional[str] = None
    status: str = Field(default="draft", index=True)
    thumbnail_url: Optional[str] = None
    duration: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    settings: Optional[str] = None
    extra_metadata: Optional[str] = Field(
        default=None, sa_column_kwargs={"name": "extra_metadata"}
    )
    permission: str = Field(default="private", index=True)


class VideoEditorAssetDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    project_id: str = Field(index=True)
    type: str = Field(index=True)
    name: str
    original_url: Optional[str] = None
    storage_url: Optional[str] = None
    extra_metadata: Optional[str] = Field(
        default=None, sa_column_kwargs={"name": "extra_metadata"}
    )
    duration: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class VideoEditorTransitionDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    project_id: str = Field(index=True)
    asset_id: str = Field(index=True)
    type: str = Field(index=True)
    start_time: float = Field(default=0.0)
    end_time: float = Field(default=0.0)
    duration: float = Field(default=0.0)
    easing: str = Field(default="linear")
    parameters: Optional[str] = None


class VideoEditorTrackDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    project_id: str = Field(index=True)
    asset_id: str = Field(index=True)
    type: str = Field(index=True)
    start_time: float = Field(default=0.0)
    end_time: float = Field(default=0.0)
    content: Optional[str] = None


class VideoEditorCaptionDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    project_id: str = Field(index=True)
    video_asset_id: str = Field(index=True)
    start_time: float = Field(default=0.0)
    end_time: float = Field(default=0.0)
    text: str = ""
    style: Optional[str] = None
    is_auto_generated: bool = Field(default=False)
    language: str = Field(default="en")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class VideoEditorKeyframeDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    project_id: str = Field(index=True)
    track_id: str = Field(index=True)
    property_name: str
    time: float
    value: str
    easing: str = Field(default="linear")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class VideoEditorColorGradeDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    project_id: str = Field(index=True)
    track_id: str = Field(index=True)
    brightness: float = Field(default=0.0)
    contrast: float = Field(default=0.0)
    saturation: float = Field(default=0.0)
    temperature: float = Field(default=0.0)
    tint: float = Field(default=0.0)
    highlights: float = Field(default=0.0)
    shadows: float = Field(default=0.0)
    vibrance: float = Field(default=0.0)
    filters: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None


class VideoEditorAudioMixDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    project_id: str = Field(index=True)
    track_id: str = Field(index=True)
    volume: float = Field(default=1.0)
    pan: float = Field(default=0.0)
    mute: bool = Field(default=False)
    solo: bool = Field(default=False)
    fade_in: float = Field(default=0.0)
    fade_out: float = Field(default=0.0)
    equalizer: Optional[str] = None
    audio_effects: Optional[str] = None
    duck_others: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None


class VideoEditorChromaKeyDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    project_id: str = Field(index=True)
    track_id: str = Field(index=True)
    enabled: bool = Field(default=False)
    key_color: str = Field(default="#00FF00")
    similarity: float = Field(default=0.4)
    smoothness: float = Field(default=0.1)
    spill_suppression: float = Field(default=0.1)
    background_type: str = Field(default="none")
    background_value: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None


class VideoEditorEffectDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    project_id: str = Field(index=True)
    track_id: str = Field(index=True)
    effect_type: str
    parameters: str
    start_time: float = Field(default=0.0)
    end_time: float = Field(default=0.0)
    enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class VideoSpeedSettingDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    project_id: str = Field(index=True)
    track_id: str = Field(index=True)
    speed: float = Field(default=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ColorGradingPresetDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    description: Optional[str] = None
    category: str = Field(index=True)
    settings: str
    is_system: bool = Field(default=False)
    creator_id: Optional[str] = Field(default=None, index=True)
    usage_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EffectLibraryDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    description: Optional[str] = None
    category: str = Field(index=True)
    effect_type: str = Field(index=True)
    parameters: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_premium: bool = Field(default=False)
    is_ar: bool = Field(default=False)
    usage_count: int = Field(default=0)
    creator_id: Optional[str] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
