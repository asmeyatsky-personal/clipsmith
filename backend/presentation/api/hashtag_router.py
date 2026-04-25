from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...application.services.hashtag_service import HashtagService
from ...domain.ports.repository_ports import HashtagRepositoryPort
from ..dependencies import get_hashtag_repo

router = APIRouter(prefix="/hashtags", tags=["hashtags"])


def get_hashtag_service(
    hashtag_repo: HashtagRepositoryPort = Depends(get_hashtag_repo),
) -> HashtagService:
    return HashtagService(hashtag_repo)


@router.get("/trending")
def get_trending_hashtags(
    hours: Annotated[
        int,
        Query(ge=1, le=168, description="Hours to look back for trending (max 7 days)"),
    ] = 24,
    limit: Annotated[
        int, Query(ge=1, le=100, description="Maximum hashtags to return")
    ] = 20,
    hashtag_service: HashtagService = Depends(get_hashtag_service),
):
    """
    Get trending hashtags based on recent usage and growth.
    """
    trending_hashtags = hashtag_service.get_trending_hashtags(hours=hours)

    # Format for response
    formatted_hashtags = hashtag_service.format_hashtags_for_display(
        [h.name for h in trending_hashtags]
    )

    # Combine with scores and usage data
    response_hashtags = []
    for i, hashtag in enumerate(trending_hashtags):
        formatted = (
            formatted_hashtags[i]
            if i < len(formatted_hashtags)
            else {
                "original": f"#{hashtag.name}",
                "camel_case": hashtag.name,
                "readable": hashtag.name,
                "title_case": hashtag.name,
                "short": hashtag.name,
            }
        )

        response_hashtags.append(
            {
                "name": hashtag.name,
                "count": hashtag.count,
                "trending_score": round(hashtag.trending_score, 2),
                "last_used_at": hashtag.last_used_at.isoformat()
                if hashtag.last_used_at
                else None,
                "formatted": formatted,
                "created_at": hashtag.created_at.isoformat(),
            }
        )

    return {
        "hashtags": response_hashtags,
        "timeframe_hours": hours,
        "total": len(response_hashtags),
    }


@router.get("/popular")
def get_popular_hashtags(
    limit: Annotated[
        int, Query(ge=1, le=100, description="Maximum hashtags to return")
    ] = 20,
    hashtag_service: HashtagService = Depends(get_hashtag_service),
):
    """
    Get most popular hashtags overall.
    """
    popular_hashtags = hashtag_service.get_popular_hashtags(limit=limit)

    # Format for response
    formatted_hashtags = hashtag_service.format_hashtags_for_display(
        [h.name for h in popular_hashtags]
    )

    response_hashtags = []
    for i, hashtag in enumerate(popular_hashtags):
        formatted = (
            formatted_hashtags[i]
            if i < len(formatted_hashtags)
            else {
                "original": f"#{hashtag.name}",
                "camel_case": hashtag.name,
                "readable": hashtag.name,
                "title_case": hashtag.name,
                "short": hashtag.name,
            }
        )

        response_hashtags.append(
            {
                "name": hashtag.name,
                "count": hashtag.count,
                "formatted": formatted,
                "created_at": hashtag.created_at.isoformat(),
            }
        )

    return {"hashtags": response_hashtags, "total": len(response_hashtags)}


@router.get("/search")
def search_hashtags(
    q: Annotated[str, Query(min_length=2, description="Search query for hashtags")],
    limit: Annotated[
        int, Query(ge=1, le=50, description="Maximum suggestions to return")
    ] = 10,
    hashtag_service: HashtagService = Depends(get_hashtag_service),
):
    """
    Search for hashtags by partial match.
    """
    if not q or len(q.strip()) < 2:
        return {"hashtags": [], "total": 0, "query": q}

    suggestions = hashtag_service.get_hashtag_suggestions(q.strip(), limit)

    return {
        "hashtags": [
            {
                "name": suggestion,
                "formatted": {
                    "original": f"#{suggestion}",
                    "camel_case": suggestion,
                    "readable": suggestion,
                    "title_case": suggestion,
                    "short": suggestion,
                },
            }
            for suggestion in suggestions
        ],
        "total": len(suggestions),
        "query": q,
    }


@router.get("/recent")
def get_recent_hashtags(
    hours: Annotated[
        int, Query(ge=1, le=168, description="Hours to look back for recent hashtags")
    ] = 24,
    limit: Annotated[
        int, Query(ge=1, le=50, description="Maximum hashtags to return")
    ] = 20,
    hashtag_service: HashtagService = Depends(get_hashtag_service),
):
    """
    Get recently used hashtags.
    """
    recent_hashtags = hashtag_service.hashtag_repo.get_recent_hashtags(
        hours=hours, limit=limit
    )

    return {
        "hashtags": [
            {
                "name": hashtag.name,
                "count": hashtag.count,
                "last_used_at": hashtag.last_used_at.isoformat()
                if hashtag.last_used_at
                else None,
                "created_at": hashtag.created_at.isoformat(),
            }
            for hashtag in recent_hashtags
        ],
        "timeframe_hours": hours,
        "total": len(recent_hashtags),
    }


@router.get("/{hashtag_name}")
def get_hashtag_details(
    hashtag_name: str,
    hashtag_repo: HashtagRepositoryPort = Depends(get_hashtag_repo),
):
    """
    Get details for a specific hashtag.
    """
    hashtag = hashtag_repo.get_by_name(hashtag_name.lower())
    if not hashtag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hashtag not found"
        )

    return {
        "name": hashtag.name,
        "count": hashtag.count,
        "trending_score": round(hashtag.trending_score, 2),
        "last_used_at": hashtag.last_used_at.isoformat()
        if hashtag.last_used_at
        else None,
        "created_at": hashtag.created_at.isoformat(),
    }
