from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from sqlmodel import Session, select
from datetime import datetime, UTC
import uuid
from ..dependencies import db_models  # legacy ORM access
from ..dependencies import get_session_for_router as get_session
from ..dependencies import get_current_user

CollaborativeVideoDB = db_models.CollaborativeVideoDB
DirectMessageDB = db_models.DirectMessageDB
DuetDB = db_models.DuetDB
LiveStreamDB = db_models.LiveStreamDB
LiveStreamGuestDB = db_models.LiveStreamGuestDB
VideoCollaboratorDB = db_models.VideoCollaboratorDB
WatchPartyDB = db_models.WatchPartyDB
WatchPartyParticipantDB = db_models.WatchPartyParticipantDB

router = APIRouter(prefix="/api/social", tags=["social"])


# ==================== Duet Endpoints ====================


@router.post("/duets")
def create_duet(
    request_body: dict,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a duet with another video."""

    original_video_id = request_body.get("original_video_id")
    response_video_id = request_body.get("response_video_id")
    duet_type = request_body.get("duet_type", "side_by_side")

    if not original_video_id or not response_video_id:
        raise HTTPException(
            status_code=400, detail="Both original_video_id and response_video_id are required"
        )

    duet = DuetDB(
        id=str(uuid.uuid4()),
        original_video_id=original_video_id,
        response_video_id=response_video_id,
        duet_type=duet_type,
        creator_id=current_user.id,
    )
    session.add(duet)
    session.commit()

    try:
        from ..dependencies import compose_duet_task, get_video_queue
        get_video_queue().enqueue(compose_duet_task, duet.id)
    except Exception:
        pass  # Compose can be retried; row is persisted

    return {
        "success": True,
        "duet": {
            "id": duet.id,
            "original_video_id": duet.original_video_id,
            "response_video_id": duet.response_video_id,
            "duet_type": duet.duet_type,
            "creator_id": duet.creator_id,
            "composed_url": duet.composed_url,
        },
    }


@router.get("/duets/{video_id}")
def get_duets_for_video(
    video_id: str,
    session: Session = Depends(get_session),
):
    """Get all duets associated with a video."""

    duets = session.exec(
        select(DuetDB).where(
            (DuetDB.original_video_id == video_id)
            | (DuetDB.response_video_id == video_id)
        )
    ).all()

    return {
        "success": True,
        "duets": [
            {
                "id": d.id,
                "original_video_id": d.original_video_id,
                "response_video_id": d.response_video_id,
                "duet_type": d.duet_type,
                "creator_id": d.creator_id,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in duets
        ],
    }


# ==================== Collaborative Video Endpoints ====================


@router.post("/collaborative-videos")
def create_collaborative_video(
    request_body: dict,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a collaborative video project."""

    video_id = request_body.get("video_id")
    max_participants = request_body.get("max_participants", 5)

    if not video_id:
        raise HTTPException(status_code=400, detail="video_id is required")

    collab = CollaborativeVideoDB(
        id=str(uuid.uuid4()),
        video_id=video_id,
        creator_id=current_user.id,
        max_participants=max_participants,
        status="open",
    )
    session.add(collab)
    session.commit()

    return {
        "success": True,
        "collaborative_video": {
            "id": collab.id,
            "video_id": collab.video_id,
            "creator_id": collab.creator_id,
            "max_participants": collab.max_participants,
            "status": collab.status,
        },
    }


@router.post("/collaborative-videos/{collab_id}/join")
def join_collaborative_video(
    collab_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Join a collaborative video project."""

    collab = session.get(CollaborativeVideoDB, collab_id)
    if not collab:
        raise HTTPException(status_code=404, detail="Collaborative video not found")

    if collab.status != "open":
        raise HTTPException(status_code=400, detail="Collaborative video is not open for participants")

    # Check existing participation
    existing = session.exec(
        select(VideoCollaboratorDB).where(
            VideoCollaboratorDB.collaborative_video_id == collab_id,
            VideoCollaboratorDB.user_id == current_user.id,
        )
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already a participant")

    participant = VideoCollaboratorDB(
        id=str(uuid.uuid4()),
        collaborative_video_id=collab_id,
        user_id=current_user.id,
    )
    session.add(participant)
    session.commit()

    return {"success": True, "message": "Joined collaborative video"}


# ==================== Live Stream Endpoints ====================


@router.post("/live-streams")
def start_live_stream(
    request_body: dict,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Start a new live stream."""

    title = request_body.get("title")
    description = request_body.get("description", "")
    scheduled_for_str = request_body.get("scheduled_for")

    if not title:
        raise HTTPException(status_code=400, detail="Title is required")

    scheduled_for = None
    if scheduled_for_str:
        try:
            scheduled_for = datetime.fromisoformat(scheduled_for_str)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid scheduled_for format. Use ISO 8601.")

    stream = LiveStreamDB(
        id=str(uuid.uuid4()),
        title=title,
        description=description,
        creator_id=current_user.id,
        status="live" if not scheduled_for else "scheduled",
        scheduled_for=scheduled_for,
    )
    session.add(stream)
    session.commit()

    from ..dependencies import get_live_stream_adapter
    sfu = get_live_stream_adapter()
    sfu.create_room(stream.id)
    host_token = sfu.issue_join_token(stream.id, current_user.id, role="host")

    return {
        "success": True,
        "live_stream": {
            "id": stream.id,
            "title": stream.title,
            "status": stream.status,
            "creator_id": stream.creator_id,
            "scheduled_for": stream.scheduled_for,
            "host_token": host_token,
        },
    }


@router.post("/live-streams/{stream_id}/join-token")
def issue_live_stream_join_token(
    stream_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Issue a viewer/guest join token for a live stream."""
    stream = session.get(LiveStreamDB, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Live stream not found")
    if stream.status not in {"scheduled", "live"}:
        raise HTTPException(status_code=400, detail="Stream not joinable")
    role = "host" if stream.creator_id == current_user.id else "viewer"
    from ..dependencies import get_live_stream_adapter
    token = get_live_stream_adapter().issue_join_token(stream_id, current_user.id, role)
    return {"success": True, "token": token, "role": role, "stream_id": stream_id}


@router.post("/live-streams/{stream_id}/end")
def end_live_stream(
    stream_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """End a live stream."""

    stream = session.get(LiveStreamDB, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Live stream not found")

    if stream.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the host can end the stream")

    if stream.status == "ended":
        raise HTTPException(status_code=400, detail="Stream has already ended")

    stream.status = "ended"
    stream.ended_at = datetime.now(UTC)
    session.add(stream)
    session.commit()

    from ..dependencies import get_live_stream_adapter
    get_live_stream_adapter().end_room(stream_id)

    return {"success": True, "message": "Live stream ended"}


@router.post("/live-streams/{stream_id}/guests")
def join_as_guest(
    stream_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Join a live stream as a guest."""

    stream = session.get(LiveStreamDB, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Live stream not found")

    if stream.status != "live":
        raise HTTPException(status_code=400, detail="Stream is not currently live")

    existing = session.exec(
        select(LiveStreamGuestDB).where(
            LiveStreamGuestDB.stream_id == stream_id,
            LiveStreamGuestDB.user_id == current_user.id,
        )
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already joined as guest")

    guest = LiveStreamGuestDB(
        id=str(uuid.uuid4()),
        stream_id=stream_id,
        user_id=current_user.id,
    )
    session.add(guest)
    session.commit()

    return {"success": True, "message": "Joined as guest"}


@router.get("/live-streams")
def list_live_streams(
    status: Optional[str] = Query(None, description="Filter by status: live, scheduled, ended"),
    session: Session = Depends(get_session),
):
    """List live streams, optionally filtered by status."""

    query = select(LiveStreamDB)
    if status:
        query = query.where(LiveStreamDB.status == status)

    streams = session.exec(query).all()

    return {
        "success": True,
        "live_streams": [
            {
                "id": s.id,
                "title": s.title,
                "description": s.description,
                "creator_id": s.creator_id,
                "status": s.status,
                "scheduled_for": s.scheduled_for,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in streams
        ],
    }


# ==================== Watch Party Endpoints ====================


@router.get("/watch-parties")
def list_watch_parties(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: active, ended"),
    session: Session = Depends(get_session),
):
    """List watch parties, optionally filtered by status."""

    query = select(WatchPartyDB)
    if status_filter:
        query = query.where(WatchPartyDB.status == status_filter)

    parties = session.exec(query).all()

    return {
        "success": True,
        "watch_parties": [
            {
                "id": p.id,
                "video_id": p.video_id,
                "title": p.title,
                "host_id": p.host_id,
                "status": p.status,
            }
            for p in parties
        ],
    }


@router.post("/watch-parties")
def create_watch_party(
    request_body: dict,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a watch party for viewing a video together."""

    video_id = request_body.get("video_id")
    title = request_body.get("title")

    if not video_id:
        raise HTTPException(status_code=400, detail="video_id is required")
    if not title:
        raise HTTPException(status_code=400, detail="title is required")

    party = WatchPartyDB(
        id=str(uuid.uuid4()),
        video_id=video_id,
        title=title,
        host_id=current_user.id,
        status="active",
    )
    session.add(party)
    session.commit()

    return {
        "success": True,
        "watch_party": {
            "id": party.id,
            "video_id": party.video_id,
            "title": party.title,
            "host_id": party.host_id,
            "status": party.status,
        },
    }


@router.post("/watch-parties/{party_id}/join")
def join_watch_party(
    party_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Join a watch party."""

    party = session.get(WatchPartyDB, party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Watch party not found")

    if party.status != "active":
        raise HTTPException(status_code=400, detail="Watch party is not active")

    existing = session.exec(
        select(WatchPartyParticipantDB).where(
            WatchPartyParticipantDB.party_id == party_id,
            WatchPartyParticipantDB.user_id == current_user.id,
        )
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already in this watch party")

    participant = WatchPartyParticipantDB(
        id=str(uuid.uuid4()),
        party_id=party_id,
        user_id=current_user.id,
    )
    session.add(participant)
    session.commit()

    return {"success": True, "message": "Joined watch party"}


# ==================== Messaging Endpoints ====================


@router.post("/messages")
def send_message(
    request_body: dict,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Send a direct message to another user."""

    receiver_id = request_body.get("receiver_id")
    content = request_body.get("content")

    if not receiver_id:
        raise HTTPException(status_code=400, detail="receiver_id is required")
    if not content:
        raise HTTPException(status_code=400, detail="content is required")

    if receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send a message to yourself")

    # Create a conversation ID from sorted user IDs for consistency
    sorted_ids = sorted([current_user.id, receiver_id])
    conversation_id = f"{sorted_ids[0]}_{sorted_ids[1]}"

    message = DirectMessageDB(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        sender_id=current_user.id,
        receiver_id=receiver_id,
        content=content,
    )
    session.add(message)
    session.commit()

    return {
        "success": True,
        "message": {
            "id": message.id,
            "conversation_id": message.conversation_id,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "content": message.content,
            "created_at": message.created_at.isoformat() if message.created_at else None,
        },
    }


@router.get("/conversations")
def get_conversations(
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get all conversations for the current user."""

    messages = session.exec(
        select(DirectMessageDB).where(
            (DirectMessageDB.sender_id == current_user.id)
            | (DirectMessageDB.receiver_id == current_user.id)
        )
    ).all()

    # Group by conversation_id and get the latest message
    conversations = {}
    for msg in messages:
        if msg.conversation_id not in conversations:
            conversations[msg.conversation_id] = {
                "conversation_id": msg.conversation_id,
                "last_message": msg.content,
                "last_message_at": msg.created_at.isoformat() if msg.created_at else None,
                "other_user_id": msg.receiver_id if msg.sender_id == current_user.id else msg.sender_id,
            }
        else:
            existing_time = conversations[msg.conversation_id].get("last_message_at")
            current_time = msg.created_at.isoformat() if msg.created_at else None
            if current_time and (not existing_time or current_time > existing_time):
                conversations[msg.conversation_id]["last_message"] = msg.content
                conversations[msg.conversation_id]["last_message_at"] = current_time

    return {"success": True, "conversations": list(conversations.values())}


@router.get("/conversations/{conversation_id}/messages")
def get_messages(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=200),
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get messages in a conversation."""

    # Verify the user is part of this conversation
    messages = session.exec(
        select(DirectMessageDB)
        .where(DirectMessageDB.conversation_id == conversation_id)
        .limit(limit)
    ).all()

    if messages and messages[0].sender_id != current_user.id and messages[0].receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to this conversation")

    return {
        "success": True,
        "messages": [
            {
                "id": m.id,
                "sender_id": m.sender_id,
                "receiver_id": m.receiver_id,
                "content": m.content,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ],
    }
