"""Phase 4–5 routers were originally written with `request_body: dict`
to ship fast. This module retrofits Pydantic schemas onto the highest-
traffic endpoints (social + community + engagement + discovery + effects).

Each schema lives next to the request shape it documents so OpenAPI clients,
the frontend type generator, and validation all line up.
"""
from __future__ import annotations

from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict


# --- Social ---------------------------------------------------------------

class CreateDuetRequest(BaseModel):
    # `extra=allow` so legacy callers (e.g. older mobile clients) sending
    # extra fields don't get a 422; we just ignore them.
    model_config = ConfigDict(extra="ignore")
    original_video_id: str = Field(min_length=1)
    response_video_id: str = Field(min_length=1)
    duet_type: str = "side_by_side"


class CreateLiveStreamRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=5000)
    scheduled_for: Optional[str] = None  # ISO 8601


class CreateWatchPartyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    video_id: str = Field(min_length=1)
    title: str = Field(min_length=1, max_length=200)


class CreateCollabRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    video_id: str = Field(min_length=1)
    max_participants: int = Field(default=4, ge=2, le=4)


class SendMessageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    receiver_id: str = Field(min_length=1)
    content: str = Field(min_length=1, max_length=5000)


# --- Community ------------------------------------------------------------

class CreateGroupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=5000)
    rules: Optional[str] = Field(default=None, max_length=5000)
    is_public: bool = True


class CreateDiscussionPostRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    content: str = Field(min_length=1, max_length=10000)
    parent_id: Optional[str] = None


class CreateCircleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=5000)


class CreateEventRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=5000)
    event_type: Literal["meetup", "workshop", "livestream", "contest"] = "meetup"
    start_time: str
    end_time: Optional[str] = None
    location: Optional[str] = Field(default=None, max_length=500)
    max_attendees: int = 0
    group_id: Optional[str] = None


class RsvpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rsvp_status: Literal["going", "interested", "not_going"] = "going"


# --- Engagement -----------------------------------------------------------

class PollOptionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1, max_length=200)
    is_correct: bool = False


class CreatePollRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    video_id: str = Field(min_length=1)
    question: str = Field(min_length=1, max_length=500)
    poll_type: Literal["single", "multiple", "quiz"] = "single"
    correct_answer: Optional[str] = None
    start_time: float = Field(ge=0)
    end_time: float = Field(gt=0)
    options: List[PollOptionInput] = Field(min_length=2, max_length=10)


class PollVoteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    option_id: str = Field(min_length=1)


class CreateChapterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=200)
    start_time: float = Field(ge=0)
    end_time: float = Field(gt=0)
    thumbnail_url: Optional[str] = None


# --- Effects --------------------------------------------------------------

class SubmitEffectRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=2000)
    category: str = Field(default="user", max_length=50)
    effect_type: Literal["shader", "facemesh", "segmentation", "transform"] = "shader"
    parameters: Optional[dict] = None
    thumbnail_url: Optional[str] = None
    is_premium: bool = False
    is_ar: bool = False
