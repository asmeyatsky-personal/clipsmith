"""Placeholder LiveStreamPort adapter.

Returns deterministic tokens so the contract is exercised in tests and the
frontend can wire the JOIN flow before Mediasoup is provisioned. Replace
with a real adapter (Mediasoup REST, LiveKit, 100ms) once the VPS is up.
"""
import hmac
import hashlib
import os
import time

from ...domain.ports.live_stream_port import LiveStreamPort


class PlaceholderLiveStreamAdapter(LiveStreamPort):
    def __init__(self, secret: str | None = None) -> None:
        self._secret = (secret or os.getenv("LIVE_STREAM_SECRET", "dev-only")).encode()

    def create_room(self, stream_id: str) -> str:
        return f"placeholder-room::{stream_id}"

    def issue_join_token(self, stream_id: str, user_id: str, role: str) -> str:
        ts = str(int(time.time()))
        msg = f"{stream_id}|{user_id}|{role}|{ts}".encode()
        sig = hmac.new(self._secret, msg, hashlib.sha256).hexdigest()[:32]
        return f"{ts}.{role}.{sig}"

    def end_room(self, stream_id: str) -> None:  # noqa: D401
        return None
