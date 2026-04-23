from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime, UTC
import uuid


class VideoAnalyticsDB(SQLModel, table=True):
    __tablename__ = "video_analytics"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    video_id: str = Field(index=True)
    user_id: str = Field(index=True)
    views: int = Field(default=0)
    likes: int = Field(default=0)
    comments: int = Field(default=0)
    shares: int = Field(default=0)
    tips_count: int = Field(default=0)
    tips_amount: float = Field(default=0.0)
    watch_time: float = Field(default=0.0)
    average_watch_time: float = Field(default=0.0)
    engagement_rate: float = Field(default=0.0)
    reach: int = Field(default=0)
    impressions: int = Field(default=0)
    period_start: datetime
    period_end: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CreatorAnalyticsDB(SQLModel, table=True):
    __tablename__ = "creator_analytics"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    period: str = Field(index=True)
    period_start: datetime
    period_end: datetime
    total_followers: int = Field(default=0)
    new_followers: int = Field(default=0)
    follower_growth_rate: float = Field(default=0.0)
    total_videos: int = Field(default=0)
    total_views: int = Field(default=0)
    total_likes: int = Field(default=0)
    total_comments: int = Field(default=0)
    total_shares: int = Field(default=0)
    average_engagement_rate: float = Field(default=0.0)
    top_performing_videos: Optional[str] = None
    total_tips: float = Field(default=0.0)
    total_subscriptions: float = Field(default=0.0)
    total_revenue: float = Field(default=0.0)
    average_revenue_per_follower: float = Field(default=0.0)
    most_viewed_video: Optional[str] = None
    most_liked_video: Optional[str] = None
    most_commented_video: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None


class TimeSeriesDataDB(SQLModel, table=True):
    __tablename__ = "time_series_data"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    metric_type: str = Field(index=True)
    time_period: str = Field(index=True)
    data_points: Optional[str] = None
    period_start: datetime
    period_end: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AudienceDemographicsDB(SQLModel, table=True):
    __tablename__ = "audience_demographics"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    age_groups: Optional[str] = None
    gender_distribution: Optional[str] = None
    location_distribution: Optional[str] = None
    device_distribution: Optional[str] = None
    language_distribution: Optional[str] = None
    period_start: datetime
    period_end: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ContentPerformanceDB(SQLModel, table=True):
    __tablename__ = "content_performance"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    video_id: str = Field(index=True)
    content_type: str = Field(index=True)
    views: int = Field(default=0)
    views_per_day: float = Field(default=0.0)
    retention_rate: float = Field(default=0.0)
    click_through_rate: float = Field(default=0.0)
    likes: int = Field(default=0)
    comments: int = Field(default=0)
    shares: int = Field(default=0)
    saves: int = Field(default=0)
    tips_amount: float = Field(default=0.0)
    subscription_conversions: int = Field(default=0)
    peak_view_time: Optional[datetime] = None
    publish_date: datetime
    first_24h_views: int = Field(default=0)
    first_7d_views: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None


class ProjectMonetizationDB(SQLModel, table=True):
    __tablename__ = "project_monetization"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    project_id: str = Field(unique=True, index=True)
    tips_enabled: bool = Field(default=True)
    subscriptions_enabled: bool = Field(default=False)
    suggested_tip_amounts: str = Field(default="[1, 5, 10, 20]")
    subscription_price: float = Field(default=9.99)
    subscription_tier_name: str = Field(default="Premium")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None


class TrafficSourceDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    video_id: str = Field(index=True)
    source_type: str = Field(index=True)
    referrer_url: Optional[str] = None
    user_id: Optional[str] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RetentionDataDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    video_id: str = Field(index=True)
    second_offset: int
    viewer_count: int = Field(default=0)
    drop_off_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PostingTimeRecommendationDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    day_of_week: int
    hour: int
    engagement_score: float = Field(default=0.0)
    sample_size: int = Field(default=0)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
