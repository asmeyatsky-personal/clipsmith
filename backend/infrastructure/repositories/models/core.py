from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, UTC
import uuid


class UserDB(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    username: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    transactions: List["TransactionDB"] = Relationship(back_populates="user")
    wallet: Optional["CreatorWalletDB"] = Relationship(back_populates="user")


class VideoDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str
    description: str
    creator_id: str = Field(index=True)
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    status: str = Field(default="PENDING")
    views: int = Field(default=0)
    likes: int = Field(default=0)
    duration: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class LikeDB(SQLModel, table=True):
    user_id: str = Field(primary_key=True)
    video_id: str = Field(primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CommentDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    video_id: str = Field(index=True)
    content: str
    username: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CaptionDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    video_id: str = Field(index=True)
    text: str
    start_time: float
    end_time: float
    language: str = Field(default="en")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TipDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    sender_id: str = Field(index=True)
    receiver_id: str = Field(index=True)
    video_id: Optional[str] = Field(default=None, index=True)
    amount: float
    currency: str = Field(default="USD")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class FollowDB(SQLModel, table=True):
    follower_id: str = Field(primary_key=True, index=True)
    followed_id: str = Field(primary_key=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class UserBlockDB(SQLModel, table=True):
    """A blocks B: A's feed/profile views must hide B's content; B can't
    interact with A. Apple App Store Guideline 1.2.
    """
    __tablename__ = "user_block"
    blocker_id: str = Field(primary_key=True, index=True)
    blocked_id: str = Field(primary_key=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PasswordResetDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    token: str = Field(unique=True, index=True)
    expires_at: datetime
    used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class NotificationDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    type: str = Field(index=True)
    title: str
    message: str
    data: Optional[str] = None
    status: str = Field(default="unread", index=True)
    read_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class HashtagDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(unique=True, index=True)
    count: int = Field(default=0)
    trending_score: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_used_at: Optional[datetime] = None
