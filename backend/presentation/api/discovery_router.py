from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import math
import uuid
from ..dependencies import db_models  # legacy ORM access
from ..dependencies import get_session_for_router as get_session
from ..dependencies import get_current_user

VideoDB = db_models.VideoDB
FavoriteCreatorDB = db_models.FavoriteCreatorDB
PlaylistCollaboratorDB = db_models.PlaylistCollaboratorDB
PlaylistDB = db_models.PlaylistDB
PlaylistItemDB = db_models.PlaylistItemDB
UserPreferencesDB = db_models.UserPreferencesDB

router = APIRouter(prefix="/api/discovery", tags=["discovery"])


# ==================== Playlist Endpoints ====================


@router.post("/playlists")
def create_playlist(
    request_body: dict,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a new playlist."""

    title = request_body.get("title")
    description = request_body.get("description", "")
    is_collaborative = request_body.get("is_collaborative", False)
    is_public = request_body.get("is_public", True)

    if not title:
        raise HTTPException(status_code=400, detail="title is required")

    playlist = PlaylistDB(
        id=str(uuid.uuid4()),
        title=title,
        description=description,
        is_collaborative=is_collaborative,
        is_public=is_public,
        creator_id=current_user.id,
    )
    session.add(playlist)
    session.commit()

    return {
        "success": True,
        "playlist": {
            "id": playlist.id,
            "title": playlist.title,
            "description": playlist.description,
            "is_collaborative": playlist.is_collaborative,
            "is_public": playlist.is_public,
            "creator_id": playlist.creator_id,
        },
    }


@router.get("/playlists")
def get_user_playlists(
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get all playlists owned by the current user."""

    playlists = session.exec(
        select(PlaylistDB).where(PlaylistDB.creator_id == current_user.id)
    ).all()

    return {
        "success": True,
        "playlists": [
            {
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "is_collaborative": p.is_collaborative,
                "is_public": p.is_public,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in playlists
        ],
    }


@router.get("/playlists/{playlist_id}")
def get_playlist(
    playlist_id: str,
    session: Session = Depends(get_session),
):
    """Get a specific playlist with its items."""

    playlist = session.get(PlaylistDB, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    items = session.exec(
        select(PlaylistItemDB).where(PlaylistItemDB.playlist_id == playlist_id)
    ).all()

    return {
        "success": True,
        "playlist": {
            "id": playlist.id,
            "title": playlist.title,
            "description": playlist.description,
            "is_collaborative": playlist.is_collaborative,
            "is_public": playlist.is_public,
            "creator_id": playlist.creator_id,
            "items": [
                {
                    "id": item.id,
                    "video_id": item.video_id,
                    "position": item.position,
                    "added_at": item.created_at.isoformat() if item.created_at else None,
                }
                for item in items
            ],
        },
    }


@router.post("/playlists/{playlist_id}/items")
def add_to_playlist(
    playlist_id: str,
    request_body: dict,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Add a video to a playlist."""

    playlist = session.get(PlaylistDB, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    # Check ownership or collaborator access
    is_owner = playlist.creator_id == current_user.id
    is_collaborator = False
    if not is_owner and playlist.is_collaborative:
        collab = session.exec(
            select(PlaylistCollaboratorDB).where(
                PlaylistCollaboratorDB.playlist_id == playlist_id,
                PlaylistCollaboratorDB.user_id == current_user.id,
            )
        ).first()
        is_collaborator = collab is not None

    if not is_owner and not is_collaborator:
        raise HTTPException(status_code=403, detail="Access denied")

    video_id = request_body.get("video_id")
    if not video_id:
        raise HTTPException(status_code=400, detail="video_id is required")

    # Get next position
    existing_items = session.exec(
        select(PlaylistItemDB).where(PlaylistItemDB.playlist_id == playlist_id)
    ).all()
    next_position = len(existing_items)

    item = PlaylistItemDB(
        id=str(uuid.uuid4()),
        playlist_id=playlist_id,
        video_id=video_id,
        position=next_position,
        added_by=current_user.id,
    )
    session.add(item)
    session.commit()

    return {"success": True, "item_id": item.id, "position": item.position}


@router.delete("/playlists/{playlist_id}/items/{video_id}")
def remove_from_playlist(
    playlist_id: str,
    video_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Remove a video from a playlist."""

    playlist = session.get(PlaylistDB, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    if playlist.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the playlist owner can remove items")

    item = session.exec(
        select(PlaylistItemDB).where(
            PlaylistItemDB.playlist_id == playlist_id,
            PlaylistItemDB.video_id == video_id,
        )
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found in playlist")

    session.delete(item)
    session.commit()

    return {"success": True, "message": "Item removed from playlist"}


@router.post("/playlists/{playlist_id}/collaborators")
def add_collaborator(
    playlist_id: str,
    request_body: dict,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Add a collaborator to a playlist."""

    playlist = session.get(PlaylistDB, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    if playlist.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the playlist owner can add collaborators")

    if not playlist.is_collaborative:
        raise HTTPException(status_code=400, detail="Playlist is not collaborative")

    user_id = request_body.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    existing = session.exec(
        select(PlaylistCollaboratorDB).where(
            PlaylistCollaboratorDB.playlist_id == playlist_id,
            PlaylistCollaboratorDB.user_id == user_id,
        )
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="User is already a collaborator")

    collaborator = PlaylistCollaboratorDB(
        id=str(uuid.uuid4()),
        playlist_id=playlist_id,
        user_id=user_id,
    )
    session.add(collaborator)
    session.commit()

    return {"success": True, "message": "Collaborator added"}


# ==================== User Preferences Endpoints ====================


@router.put("/preferences")
def update_user_preferences(
    request_body: dict,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update user discovery preferences."""

    existing = session.exec(
        select(UserPreferencesDB).where(
            UserPreferencesDB.user_id == current_user.id
        )
    ).first()

    if existing:
        existing.interest_weight = request_body.get("interest_weight", existing.interest_weight)
        existing.community_weight = request_body.get("community_weight", existing.community_weight)
        existing.virality_weight = request_body.get("virality_weight", existing.virality_weight)
        existing.freshness_weight = request_body.get("freshness_weight", existing.freshness_weight)
        existing.preferred_categories = request_body.get("preferred_categories", existing.preferred_categories)
        existing.preferred_languages = request_body.get("preferred_languages", existing.preferred_languages)
        existing.location = request_body.get("location", existing.location)
        session.add(existing)
    else:
        prefs = UserPreferencesDB(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            interest_weight=request_body.get("interest_weight", 0.5),
            community_weight=request_body.get("community_weight", 0.2),
            virality_weight=request_body.get("virality_weight", 0.2),
            freshness_weight=request_body.get("freshness_weight", 0.1),
            preferred_categories=request_body.get("preferred_categories", ""),
            preferred_languages=request_body.get("preferred_languages", ""),
            location=request_body.get("location", ""),
        )
        session.add(prefs)

    session.commit()

    return {"success": True, "message": "Preferences updated"}


@router.get("/preferences")
def get_user_preferences(
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get user discovery preferences."""

    prefs = session.exec(
        select(UserPreferencesDB).where(
            UserPreferencesDB.user_id == current_user.id
        )
    ).first()

    if not prefs:
        return {
            "success": True,
            "preferences": {
                "interest_weight": 0.5,
                "community_weight": 0.2,
                "virality_weight": 0.2,
                "freshness_weight": 0.1,
                "preferred_categories": "",
                "preferred_languages": "",
                "location": "",
            },
        }

    return {
        "success": True,
        "preferences": {
            "interest_weight": prefs.interest_weight,
            "community_weight": prefs.community_weight,
            "virality_weight": prefs.virality_weight,
            "freshness_weight": prefs.freshness_weight,
            "preferred_categories": prefs.preferred_categories,
            "preferred_languages": prefs.preferred_languages,
            "location": prefs.location,
        },
    }


# ==================== Favorite Creator Endpoints ====================


@router.post("/favorites")
def add_favorite_creator(
    request_body: dict,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Add a creator to favorites."""

    creator_id = request_body.get("creator_id")
    priority_notifications = request_body.get("priority_notifications", True)

    if not creator_id:
        raise HTTPException(status_code=400, detail="creator_id is required")

    if creator_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot favorite yourself")

    existing = session.exec(
        select(FavoriteCreatorDB).where(
            FavoriteCreatorDB.user_id == current_user.id,
            FavoriteCreatorDB.creator_id == creator_id,
        )
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Creator is already in favorites")

    favorite = FavoriteCreatorDB(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        creator_id=creator_id,
        priority_notifications=priority_notifications,
    )
    session.add(favorite)
    session.commit()

    return {"success": True, "message": "Creator added to favorites"}


@router.delete("/favorites/{creator_id}")
def remove_favorite_creator(
    creator_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Remove a creator from favorites."""

    favorite = session.exec(
        select(FavoriteCreatorDB).where(
            FavoriteCreatorDB.user_id == current_user.id,
            FavoriteCreatorDB.creator_id == creator_id,
        )
    ).first()

    if not favorite:
        raise HTTPException(status_code=404, detail="Creator not found in favorites")

    session.delete(favorite)
    session.commit()

    return {"success": True, "message": "Creator removed from favorites"}


@router.get("/favorites")
def get_favorite_creators(
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get user's favorite creators."""

    favorites = session.exec(
        select(FavoriteCreatorDB).where(
            FavoriteCreatorDB.user_id == current_user.id
        )
    ).all()

    return {
        "success": True,
        "favorites": [
            {
                "id": f.id,
                "creator_id": f.creator_id,
                "priority_notifications": f.priority_notifications,
                "added_at": f.created_at.isoformat() if f.created_at else None,
            }
            for f in favorites
        ],
    }


# ==================== Discovery Score Endpoints ====================


@router.get("/videos/{video_id}/discovery-score")
def calculate_discovery_score(
    video_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Calculate a discovery score for a video based on user preferences."""

    prefs = session.exec(
        select(UserPreferencesDB).where(
            UserPreferencesDB.user_id == current_user.id
        )
    ).first()

    interest_weight = prefs.interest_weight if prefs else 0.5
    community_weight = prefs.community_weight if prefs else 0.2
    virality_weight = prefs.virality_weight if prefs else 0.2
    freshness_weight = prefs.freshness_weight if prefs else 0.1

    video = session.get(VideoDB, video_id)
    if video is None:
        # Soft-miss: return a zeroed scorecard so callers can still render.
        return {
            "success": True,
            "video_id": video_id,
            "discovery_score": 0.0,
            "feature_contributions": {"interest": 0, "community": 0, "virality": 0, "freshness": 0},
            "weights_applied": {
                "interest": interest_weight,
                "community": community_weight,
                "virality": virality_weight,
                "freshness": freshness_weight,
            },
        }

    # Per-feature signals, each normalised to [0, 1].
    views = max(int(video.views or 0), 0)
    likes = max(int(video.likes or 0), 0)
    virality = math.log1p(views) / math.log1p(1_000_000)
    interest = min(likes / 1000.0, 1.0)
    community = 1.0 if session.exec(
        select(FavoriteCreatorDB).where(
            FavoriteCreatorDB.user_id == current_user.id,
            FavoriteCreatorDB.creator_id == video.creator_id,
        )
    ).first() else 0.0
    created = video.created_at
    if created and created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    age_hours = (
        (datetime.now(timezone.utc) - created).total_seconds() / 3600.0
        if created else 0.0
    )
    # Half-life ~72h: a 3-day-old video scores ~0.5 on freshness.
    freshness = math.exp(-age_hours / 72.0)

    score = (
        interest_weight * interest
        + community_weight * community
        + virality_weight * virality
        + freshness_weight * freshness
    )

    return {
        "success": True,
        "video_id": video_id,
        "discovery_score": round(min(max(score, 0.0), 1.0), 4),
        "feature_contributions": {
            "interest": round(interest, 4),
            "community": round(community, 4),
            "virality": round(virality, 4),
            "freshness": round(freshness, 4),
        },
        "weights_applied": {
            "interest": interest_weight,
            "community": community_weight,
            "virality": virality_weight,
            "freshness": freshness_weight,
        },
    }


@router.get("/videos/{video_id}/traffic")
def get_traffic_breakdown(
    video_id: str,
    session: Session = Depends(get_session),
):
    """Get traffic source breakdown for a video."""
    # Placeholder - would integrate with analytics tracking
    return {
        "success": True,
        "video_id": video_id,
        "traffic": {
            "feed": 0,
            "search": 0,
            "profile": 0,
            "direct": 0,
            "external": 0,
            "hashtag": 0,
        },
    }


@router.get("/videos/{video_id}/retention")
def get_retention_graph(
    video_id: str,
    session: Session = Depends(get_session),
):
    """Get retention graph data for a video."""
    # Placeholder - would integrate with video player analytics
    return {
        "success": True,
        "video_id": video_id,
        "retention": {
            "data_points": [],
            "average_watch_time": 0,
            "average_percentage": 0,
        },
    }


@router.get("/posting-recommendations")
def get_posting_recommendations(
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Best-posting-time recommendations from the creator's own video history.

    Aggregates the creator's videos by (weekday, hour-bucket) and ranks
    each cell by mean (views + 5*likes), a quick engagement proxy. Cells
    needing >=2 samples to count; falls back to global heuristics when
    history is sparse.
    """
    videos = session.exec(
        select(VideoDB).where(VideoDB.creator_id == current_user.id)
    ).all()

    buckets: dict[tuple[int, int], list[float]] = defaultdict(list)
    for v in videos:
        if not v.created_at:
            continue
        ts = v.created_at if v.created_at.tzinfo else v.created_at.replace(tzinfo=timezone.utc)
        score = float(v.views or 0) + 5.0 * float(v.likes or 0)
        buckets[(ts.weekday(), ts.hour)].append(score)

    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    ranked = sorted(
        (
            (weekdays[wd], hr, sum(scores) / len(scores))
            for (wd, hr), scores in buckets.items()
            if len(scores) >= 2
        ),
        key=lambda t: t[2],
        reverse=True,
    )

    if ranked:
        best = [{"day": d, "hour": h, "score": round(s, 2), "timezone": "UTC"} for d, h, s in ranked[:5]]
    else:
        best = [
            {"day": "Wednesday", "hour": 12, "timezone": "UTC", "score": None},
            {"day": "Friday", "hour": 17, "timezone": "UTC", "score": None},
            {"day": "Sunday", "hour": 19, "timezone": "UTC", "score": None},
        ]

    audience_hours = sorted(
        {h for (_, h), scores in buckets.items() if len(scores) >= 2}
    )

    return {
        "success": True,
        "recommendations": {
            "best_posting_times": best,
            "trending_topics": [],
            "audience_active_hours": audience_hours,
            "suggested_hashtags": [],
            "samples_analysed": sum(len(s) for s in buckets.values()),
        },
    }
