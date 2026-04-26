"""WebSocket sync for watch parties (Phase 4.2).

Each party gets a room. Connected clients broadcast play/pause/seek events
to all other participants. Auth is JWT-via-query-param so the static SPA
shell can connect without cookies.
"""
from collections import defaultdict
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status

from ..dependencies import db_models  # legacy ORM access
from ..dependencies import JWTAdapter, get_task_session

router = APIRouter(prefix="/ws/watch-parties", tags=["watch-parties-ws"])

WatchPartyDB = db_models.WatchPartyDB
WatchPartyParticipantDB = db_models.WatchPartyParticipantDB


_rooms: Dict[str, Set[WebSocket]] = defaultdict(set)


async def _broadcast(party_id: str, message: dict, sender: WebSocket) -> None:
    dead: list[WebSocket] = []
    for ws in _rooms.get(party_id, set()):
        if ws is sender:
            continue
        try:
            await ws.send_json(message)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _rooms[party_id].discard(ws)


@router.websocket("/{party_id}")
async def watch_party_ws(
    websocket: WebSocket,
    party_id: str,
    token: str = Query(...),
):
    try:
        payload = JWTAdapter.verify_token(token)
        user_id = payload.get("sub") if isinstance(payload, dict) else None
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    with get_task_session() as session:
        party = session.get(WatchPartyDB, party_id)
        if not party:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    await websocket.accept()
    _rooms[party_id].add(websocket)
    try:
        await _broadcast(party_id, {"type": "user_joined", "user_id": user_id}, websocket)
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")
            if event_type in {"play", "pause", "seek", "chat"}:
                data["user_id"] = user_id
                await _broadcast(party_id, data, websocket)
    except WebSocketDisconnect:
        pass
    finally:
        _rooms[party_id].discard(websocket)
        await _broadcast(party_id, {"type": "user_left", "user_id": user_id}, websocket)
