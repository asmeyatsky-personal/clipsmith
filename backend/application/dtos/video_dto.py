from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import List, Generic, TypeVar
from ...domain.entities.video import VideoStatus
from ..utils.sanitization import (
    sanitize_input,
    MAX_TITLE_LENGTH,
    MAX_DESCRIPTION_LENGTH,
)


class VideoCreateDTO(BaseModel):
    title: str
    description: str
    creator_id: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        if len(v) > MAX_TITLE_LENGTH:
            raise ValueError(f"Title cannot exceed {MAX_TITLE_LENGTH} characters")
        return sanitize_input(v.strip())

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        if len(v) > MAX_DESCRIPTION_LENGTH:
            raise ValueError(
                f"Description cannot exceed {MAX_DESCRIPTION_LENGTH} characters"
            )
        return sanitize_input(v.strip())


class VideoResponseDTO(BaseModel):
    id: str
    title: str
    description: str
    creator_id: str
    creator_username: str | None = None  # resolved from User repo when feed serializes
    status: VideoStatus
    url: str | None
    thumbnail_url: str | None
    views: int
    likes: int
    comments: int = 0  # comment count badge
    duration: float
    # Pydantic 2 will accept either str or datetime here and serialize as ISO 8601.
    created_at: datetime | None = None

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


class PaginatedVideoResponseDTO(BaseModel):
    items: List[VideoResponseDTO]
    total: int
    page: int
    page_size: int
    total_pages: int
