import hashlib
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from ...application.dtos.video_dto import PaginatedVideoResponseDTO, VideoResponseDTO
from ...application.use_cases.get_personalized_feed import GetPersonalizedFeedUseCase
from ...domain.ports.repository_ports import (
    InteractionRepositoryPort,
    UserRepositoryPort,
    VideoRepositoryPort,
)
from ...domain.ports.repository_ports import FollowRepositoryPort
from ...domain.ports.security_port import JWTPort
from ...domain.ports.user_block_port import UserBlockRepositoryPort
from ..dependencies import (
    get_follow_repo,
    get_interaction_repo,
    get_jwt,
    get_user_block_repo,
    get_user_repo,
    get_video_repo,
)

router = APIRouter(prefix="/feed", tags=["feed"])


def _optional_current_user(
    request: Request,
    user_repo: UserRepositoryPort = Depends(get_user_repo),
    jwt: JWTPort = Depends(get_jwt),
):
    token = request.cookies.get("access_token") or request.headers.get(
        "Authorization", ""
    ).replace("Bearer ", "")
    if not token:
        return None
    try:
        payload = jwt.decode(token)
    except ValueError:
        return None
    user_id = payload.get("user_id") or payload.get("sub")
    if not user_id:
        return None
    return user_repo.get_by_id(user_id)


def _to_dto(
    v,
    creator_username: str | None = None,
    comment_count: int = 0,
) -> VideoResponseDTO:
    return VideoResponseDTO(
        id=v.id,
        title=v.title,
        description=v.description,
        creator_id=v.creator_id,
        creator_username=creator_username,
        url=v.url,
        thumbnail_url=v.thumbnail_url,
        status=v.status,
        views=v.views,
        likes=v.likes,
        comments=comment_count,
        duration=v.duration,
        created_at=v.created_at,
    )


def _enrich_videos(
    videos: list,
    user_repo: UserRepositoryPort,
    interaction_repo: InteractionRepositoryPort,
) -> list[VideoResponseDTO]:
    """Resolve creator usernames + comment counts in batch (avoid N+1)."""
    if not videos:
        return []
    creator_ids = list({v.creator_id for v in videos})
    usernames: dict[str, str] = {}
    for cid in creator_ids:
        u = user_repo.get_by_id(cid)
        if u:
            usernames[cid] = u.username
    comment_counts: dict[str, int] = {}
    if hasattr(interaction_repo, "count_comments_for_videos"):
        try:
            comment_counts = interaction_repo.count_comments_for_videos(
                [v.id for v in videos]
            )
        except Exception:
            pass
    return [
        _to_dto(
            v,
            creator_username=usernames.get(v.creator_id),
            comment_count=comment_counts.get(v.id, 0),
        )
        for v in videos
    ]


@router.get("/", response_model=PaginatedVideoResponseDTO)
def get_feed(
    request: Request,
    response: Response,
    feed_type: Annotated[
        str, Query(description="Feed type: foryou, following, trending")
    ] = "foryou",
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    current_user=Depends(_optional_current_user),
    video_repo: VideoRepositoryPort = Depends(get_video_repo),
    interaction_repo: InteractionRepositoryPort = Depends(get_interaction_repo),
    user_repo: UserRepositoryPort = Depends(get_user_repo),
    block_repo: UserBlockRepositoryPort = Depends(get_user_block_repo),
    follow_repo: FollowRepositoryPort = Depends(get_follow_repo),
):
    valid = ["foryou", "following", "trending"]
    if feed_type not in valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid feed type. Must be one of: {', '.join(valid)}",
        )

    if not current_user and feed_type != "trending":
        feed_type = "trending"

    use_case = GetPersonalizedFeedUseCase(
        video_repo,
        interaction_repo,
        user_repo,
        user_block_repo=block_repo,
        follow_repo=follow_repo,
    )

    if current_user:
        videos = use_case.execute(current_user.id, feed_type, page, page_size)
        total_count = use_case.get_feed_count(current_user.id, feed_type)
    else:
        videos = video_repo.find_all(offset=(page - 1) * page_size, limit=page_size)
        total_count = video_repo.count_all()

    payload = PaginatedVideoResponseDTO(
        items=_enrich_videos(videos, user_repo, interaction_repo),
        total=total_count,
        page=page,
        page_size=page_size,
        total_pages=(total_count + page_size - 1) // page_size,
    )

    # Phase 6.2 — weak ETag over the result set so clients can 304 quickly.
    # Hash only the (id, views, likes) tuple per item: cheap to compute and
    # changes the moment any counter advances.
    sig_src = "|".join(f"{v.id}:{v.views}:{v.likes}" for v in payload.items)
    # ETag is a cache key, not a security primitive — sha1 with usedforsecurity=False
    etag = 'W/"' + hashlib.sha1(  # nosec B324 — non-security checksum
        f"{feed_type}:{page}:{page_size}:{sig_src}".encode(),
        usedforsecurity=False,
    ).hexdigest() + '"'
    if request.headers.get("if-none-match") == etag:
        response.status_code = status.HTTP_304_NOT_MODIFIED
        response.headers["ETag"] = etag
        response.headers["Cache-Control"] = "private, max-age=10"
        return None  # FastAPI lets us short-circuit when 304
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "private, max-age=10"

    return payload


@router.get("/trending", response_model=PaginatedVideoResponseDTO)
def get_trending_feed(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    video_repo: VideoRepositoryPort = Depends(get_video_repo),
    interaction_repo: InteractionRepositoryPort = Depends(get_interaction_repo),
    user_repo: UserRepositoryPort = Depends(get_user_repo),
):
    all_videos = video_repo.find_all(offset=0, limit=200)
    trending = sorted(all_videos, key=lambda v: (v.views + v.likes * 5), reverse=True)
    start = (page - 1) * page_size
    paginated = trending[start : start + page_size]
    total = len(trending)
    return PaginatedVideoResponseDTO(
        items=_enrich_videos(paginated, user_repo, interaction_repo),
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/categories")
def get_categories():
    return {
        "categories": [
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
    }


@router.get("/recommended", response_model=PaginatedVideoResponseDTO)
def get_recommended_for_you(
    page: int = 1,
    page_size: int = 20,
    video_repo: VideoRepositoryPort = Depends(get_video_repo),
):
    videos = video_repo.find_all(offset=(page - 1) * page_size, limit=page_size * 3)
    recommended = sorted(videos, key=lambda v: v.views + v.likes * 5, reverse=True)[
        :page_size
    ]
    total = len(recommended)
    return PaginatedVideoResponseDTO(
        items=[_to_dto(v) for v in recommended],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/categories/{category_id}")
def get_category_feed(
    category_id: str,
    page: int = 1,
    page_size: int = 20,
    video_repo: VideoRepositoryPort = Depends(get_video_repo),
):
    valid = [
        "entertainment", "gaming", "music", "education", "sports", "comedy",
        "news", "tech", "fashion", "food", "travel", "fitness",
    ]
    if category_id not in valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {', '.join(valid)}",
        )

    all_videos = video_repo.find_all(offset=0, limit=500)
    keywords_by_cat = {
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
    kws = keywords_by_cat.get(category_id, [])
    filtered = [
        v for v in all_videos
        if any(kw in (v.title or "").lower() or kw in (v.description or "").lower() for kw in kws)
    ] or all_videos

    start = (page - 1) * page_size
    paginated = filtered[start : start + page_size]
    return PaginatedVideoResponseDTO(
        items=[_to_dto(v) for v in paginated],
        total=len(filtered),
        page=page,
        page_size=page_size,
        total_pages=(len(filtered) + page_size - 1) // page_size,
    )
