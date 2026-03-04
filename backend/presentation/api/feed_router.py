from typing import Annotated, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from ...domain.ports.repository_ports import (
    VideoRepositoryPort,
    InteractionRepositoryPort,
    UserRepositoryPort,
)
from ...infrastructure.repositories.sqlite_video_repo import SQLiteVideoRepository
from ...infrastructure.repositories.sqlite_interaction_repo import (
    SQLiteInteractionRepository,
)
from ...infrastructure.repositories.sqlite_user_repo import SQLiteUserRepository
from ...application.use_cases.get_personalized_feed import GetPersonalizedFeedUseCase
from ...application.dtos.video_dto import VideoResponseDTO, PaginatedVideoResponseDTO
from ...infrastructure.security.jwt_adapter import JWTAdapter

router = APIRouter(prefix="/feed", tags=["feed"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Dependency Injection Helpers
from ...infrastructure.repositories.database import get_session
from sqlmodel import Session


def get_video_repo(session: Session = Depends(get_session)) -> VideoRepositoryPort:
    return SQLiteVideoRepository(session)


def get_interaction_repo(
    session: Session = Depends(get_session),
) -> InteractionRepositoryPort:
    return SQLiteInteractionRepository(session)


def get_user_repo(session: Session = Depends(get_session)) -> UserRepositoryPort:
    return SQLiteUserRepository(session)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: UserRepositoryPort = Depends(get_user_repo),
):
    payload = JWTAdapter.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user = user_repo.get_by_id(payload.get("sub"))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


@router.get("/", response_model=PaginatedVideoResponseDTO)
def get_feed(
    feed_type: Annotated[
        str, Query(description="Feed type: foryou, following, trending")
    ] = "foryou",
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Videos per page")] = 20,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    video_repo: VideoRepositoryPort = Depends(get_video_repo),
    interaction_repo: InteractionRepositoryPort = Depends(get_interaction_repo),
    user_repo: UserRepositoryPort = Depends(get_user_repo),
):
    """
    Get personalized video feed.

    - **foryou**: Personalized recommendations based on viewing history and preferences
    - **following**: Videos from creators you follow
    - **trending**: Popular videos in the last 24 hours
    """

    # Validate feed type
    valid_feed_types = ["foryou", "following", "trending"]
    if feed_type not in valid_feed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid feed type. Must be one of: {', '.join(valid_feed_types)}",
        )

    # For anonymous users, only show trending
    if not current_user and feed_type != "trending":
        feed_type = "trending"

    # Get personalized feed
    feed_use_case = GetPersonalizedFeedUseCase(video_repo, interaction_repo, user_repo)

    if current_user:
        user_id = current_user.id
        videos = feed_use_case.execute(user_id, feed_type, page, page_size)
        total_count = feed_use_case.get_feed_count(user_id, feed_type)
    else:
        # For anonymous users, just return recent videos
        videos = video_repo.find_all(offset=(page - 1) * page_size, limit=page_size)
        total_count = video_repo.count_all()

    # Convert to response DTOs
    video_responses = [
        VideoResponseDTO(
            id=v.id,
            title=v.title,
            description=v.description,
            creator_id=v.creator_id,
            url=v.url,
            thumbnail_url=v.thumbnail_url,
            status=v.status,
            views=v.views,
            likes=v.likes,
            duration=v.duration,
            created_at=v.created_at,
        )
        for v in videos
    ]

    # Calculate pagination
    total_pages = (total_count + page_size - 1) // page_size

    return PaginatedVideoResponseDTO(
        items=video_responses,
        total=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/trending", response_model=PaginatedVideoResponseDTO)
def get_trending_feed(
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Videos per page")] = 20,
    video_repo: VideoRepositoryPort = Depends(get_video_repo),
):
    """
    Get trending videos from the last 24 hours.
    This endpoint doesn't require authentication.
    """
    # Fetch only the page we need, sorted by engagement at the DB level
    offset = (page - 1) * page_size
    all_videos = video_repo.find_all(offset=0, limit=200)

    # Sort by engagement score (views + likes * 5)
    trending_videos = sorted(
        all_videos, key=lambda v: (v.views + v.likes * 5), reverse=True
    )

    # Apply pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_videos = trending_videos[start_idx:end_idx]

    # Convert to response DTOs
    video_responses = [
        VideoResponseDTO(
            id=v.id,
            title=v.title,
            description=v.description,
            creator_id=v.creator_id,
            url=v.url,
            thumbnail_url=v.thumbnail_url,
            status=v.status,
            views=v.views,
            likes=v.likes,
            duration=v.duration,
            created_at=v.created_at,
        )
        for v in paginated_videos
    ]

    total_count = len(trending_videos)
    total_pages = (total_count + page_size - 1) // page_size

    return PaginatedVideoResponseDTO(
        items=video_responses,
        total=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/categories")
def get_categories(
    video_repo: VideoRepositoryPort = Depends(get_video_repo),
):
    """Get available video categories."""
    categories = [
        {"id": "entertainment", "name": "Entertainment", "icon": "🎬"},
        {"id": "gaming", "name": "Gaming", "icon": "🎮"},
        {"id": "music", "name": "Music", "icon": "🎵"},
        {"id": "education", "name": "Education", "icon": "📚"},
        {"id": "sports", "name": "Sports", "icon": "⚽"},
        {"id": "comedy", "name": "Comedy", "icon": "😂"},
        {"id": "news", "name": "News", "icon": "📰"},
        {"id": "tech", "name": "Technology", "icon": "💻"},
        {"id": "fashion", "name": "Fashion", "icon": "👗"},
        {"id": "food", "name": "Food", "icon": "🍳"},
        {"id": "travel", "name": "Travel", "icon": "✈️"},
        {"id": "fitness", "name": "Fitness", "icon": "💪"},
    ]
    return {"categories": categories}


@router.get("/recommended", response_model=PaginatedVideoResponseDTO)
def get_recommended_for_you(
    page: int = 1,
    page_size: int = 20,
    video_repo: VideoRepositoryPort = Depends(get_video_repo),
):
    """Get recommended videos based on engagement patterns."""
    videos = video_repo.find_all(offset=(page - 1) * page_size, limit=page_size * 3)

    recommended = sorted(videos, key=lambda v: v.views + v.likes * 5, reverse=True)[
        :page_size
    ]

    total_count = len(recommended)

    video_responses = [
        VideoResponseDTO(
            id=v.id,
            title=v.title,
            description=v.description,
            creator_id=v.creator_id,
            url=v.url,
            thumbnail_url=v.thumbnail_url,
            status=v.status,
            views=v.views,
            likes=v.likes,
            duration=v.duration,
            created_at=v.created_at,
        )
        for v in recommended
    ]

    return PaginatedVideoResponseDTO(
        items=video_responses,
        total=total_count,
        page=page,
        page_size=page_size,
        total_pages=(total_count + page_size - 1) // page_size,
    )


@router.get("/categories/{category_id}")
def get_category_feed(
    category_id: str,
    page: int = 1,
    page_size: int = 20,
    video_repo: VideoRepositoryPort = Depends(get_video_repo),
):
    """Get videos filtered by category."""
    valid_categories = [
        "entertainment", "gaming", "music", "education", "sports",
        "comedy", "news", "tech", "fashion", "food", "travel", "fitness",
    ]
    if category_id not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}",
        )

    # Filter videos by category (using title/description keyword matching)
    all_videos = video_repo.find_all(offset=0, limit=500)
    category_keywords = {
        "entertainment": ["entertainment", "show", "drama", "movie"],
        "gaming": ["game", "gaming", "play", "esports"],
        "music": ["music", "song", "album", "concert", "beat"],
        "education": ["learn", "tutorial", "how to", "education", "course"],
        "sports": ["sport", "game", "match", "workout", "football"],
        "comedy": ["funny", "comedy", "joke", "humor", "laugh"],
        "news": ["news", "breaking", "report", "update"],
        "tech": ["tech", "code", "programming", "software", "ai"],
        "fashion": ["fashion", "style", "outfit", "clothing"],
        "food": ["food", "recipe", "cooking", "cook", "meal"],
        "travel": ["travel", "trip", "destination", "explore"],
        "fitness": ["fitness", "workout", "exercise", "gym", "health"],
    }

    keywords = category_keywords.get(category_id, [])
    filtered = [
        v for v in all_videos
        if any(
            kw in (v.title or "").lower() or kw in (v.description or "").lower()
            for kw in keywords
        )
    ]

    # If no keyword match, fall back to returning recent videos
    if not filtered:
        filtered = all_videos

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated = filtered[start_idx:end_idx]

    video_responses = [
        VideoResponseDTO(
            id=v.id, title=v.title, description=v.description,
            creator_id=v.creator_id, url=v.url, thumbnail_url=v.thumbnail_url,
            status=v.status, views=v.views, likes=v.likes,
            duration=v.duration, created_at=v.created_at,
        )
        for v in paginated
    ]

    return PaginatedVideoResponseDTO(
        items=video_responses,
        total=len(filtered),
        page=page,
        page_size=page_size,
        total_pages=(len(filtered) + page_size - 1) // page_size,
    )
