from typing import Protocol


class LiveStreamPort(Protocol):
    """Port for the SFU (Mediasoup-style) backing live streams.

    Adapters return tokens or short-lived join URLs that the client uses
    to establish a WebRTC session against the SFU. The domain only sees
    opaque strings so we can swap Mediasoup, LiveKit, or 100ms behind it.
    """

    def create_room(self, stream_id: str) -> str:
        """Provision an SFU room. Returns an opaque room handle."""
        ...

    def issue_join_token(self, stream_id: str, user_id: str, role: str) -> str:
        """Return a short-lived token authorising the user to join."""
        ...

    def end_room(self, stream_id: str) -> None:
        """Terminate the SFU room and any active streams."""
        ...
