from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime, UTC
import uuid


class AICaptionJobDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    project_id: str = Field(index=True)
    user_id: str = Field(index=True)
    video_asset_id: str = Field(index=True)
    status: str = Field(default="pending", index=True)
    language: str = Field(default="en")
    result: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: Optional[datetime] = None


class AITemplateDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    description: Optional[str] = None
    category: str = Field(index=True)
    style: str
    thumbnail_url: Optional[str] = None
    project_data: str
    is_premium: bool = Field(default=False)
    price: float = Field(default=0.0)
    usage_count: int = Field(default=0)
    creator_id: Optional[str] = Field(index=True)
    is_public: bool = Field(default=True)
    tags: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None


class AIVideoGenerationDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    project_id: str = Field(index=True)
    user_id: str = Field(index=True)
    generation_type: str
    prompt: str
    negative_prompt: Optional[str] = None
    duration: float = Field(default=5.0)
    status: str = Field(default="pending", index=True)
    model_version: str = Field(default="v1")
    settings: Optional[str] = None
    result_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: Optional[datetime] = None


class AIVoiceOverDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    project_id: str = Field(index=True)
    user_id: str = Field(index=True)
    text: str
    voice_id: str
    language: str = Field(default="en")
    speed: float = Field(default=1.0)
    status: str = Field(default="pending", index=True)
    result_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: Optional[datetime] = None
