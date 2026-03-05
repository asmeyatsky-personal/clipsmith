import pytest
from datetime import datetime
from sqlmodel import create_engine, Session
from backend.domain.entities.user import User
from backend.domain.entities.video import Video, VideoStatus
from backend.domain.entities.payment import (
    Transaction,
    TransactionType,
    TransactionStatus,
)
from backend.domain.entities.analytics import VideoAnalytics, MetricType, TimePeriod


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    from backend.infrastructure.repositories.models import SQLModel

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(
        id="test_user_123",
        username="testuser",
        email="test@example.com",
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_video(sample_user):
    """Create a sample video for testing."""
    return Video(
        id="test_video_123",
        creator_id=sample_user.id,
        url="https://example.com/video.mp4",
        status=VideoStatus.READY,
    )


class TestBasicEntities:
    """Test basic entity creation and validation."""

    def test_user_creation(self):
        """Test user entity creation."""
        user = User(id="user_123", username="testuser", email="test@example.com")

        assert user.id == "user_123"
        assert user.username == "testuser"
        assert user.email == "test@example.com"

    def test_video_creation(self, sample_user):
        """Test video entity creation."""
        video = Video(
            id="video_123",
            creator_id=sample_user.id,
            url="https://example.com/video.mp4",
            status=VideoStatus.READY,
        )

        assert video.id == "video_123"
        assert video.creator_id == sample_user.id
        assert video.status == VideoStatus.READY

    def test_transaction_creation(self, sample_user):
        """Test transaction entity creation."""
        transaction = Transaction(
            user_id=sample_user.id,
            amount=10.0,
            transaction_type=TransactionType.TIP,
            description="Test tip transaction",
        )

        assert transaction.user_id == sample_user.id
        assert transaction.amount == 10.0
        assert transaction.transaction_type == TransactionType.TIP
        assert transaction.description == "Test tip transaction"

    def test_video_analytics_creation(self, sample_video, sample_user):
        """Test video analytics creation."""
        analytics = VideoAnalytics(
            video_id=sample_video.id,
            user_id=sample_user.id,
            views=100,
            likes=25,
            comments=5,
            shares=3,
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
        )

        assert analytics.video_id == sample_video.id
        assert analytics.user_id == sample_user.id
        assert analytics.views == 100
        assert analytics.likes == 25


class TestBusinessLogic:
    """Test business logic methods."""

    def test_transaction_completion(self):
        """Test transaction completion logic."""
        transaction = Transaction(
            id="test_transaction",
            user_id="test_user",
            amount=10.0,
            transaction_type=TransactionType.TIP,
            status=TransactionStatus.PENDING,
        )

        completed_transaction = transaction.complete()

        assert completed_transaction.status == TransactionStatus.COMPLETED
        assert completed_transaction.completed_at is not None

    def test_analytics_calculations(self):
        """Test analytics calculation methods."""
        analytics = VideoAnalytics(
            video_id="test_video",
            user_id="test_user",
            views=100,
            likes=25,
            comments=5,
            shares=3,
            watch_time=300.0,
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
        )

        engagement_rate = analytics.calculate_engagement_rate()
        expected_rate = (25 + 5 + 3) / 100 * 100  # 33%
        assert engagement_rate == expected_rate

        avg_watch_time = analytics.calculate_average_watch_time()
        assert avg_watch_time == 300.0 / 100


class TestEnums:
    """Test enum values and validation."""

    def test_transaction_types(self):
        """Test transaction type enum."""
        assert TransactionType.TIP == "tip"
        assert TransactionType.SUBSCRIPTION == "subscription"
        assert TransactionType.REFUND == "refund"

    def test_video_status(self):
        """Test video status enum."""
        assert VideoStatus.UPLOADING == "UPLOADING"
        assert VideoStatus.PROCESSING == "PROCESSING"
        assert VideoStatus.READY == "READY"
        assert VideoStatus.FAILED == "FAILED"

    def test_analytics_metrics(self):
        """Test analytics metric enum."""
        assert MetricType.VIEWS == "views"
        assert MetricType.LIKES == "likes"
        assert MetricType.COMMENTS == "comments"
        assert MetricType.SHARES == "shares"

    def test_time_periods(self):
        """Test time period enum."""
        assert TimePeriod.HOUR == "hour"
        assert TimePeriod.DAY == "day"
        assert TimePeriod.WEEK == "week"
        assert TimePeriod.MONTH == "month"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
