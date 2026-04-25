from typing import List, Optional, Dict, Any
from datetime import UTC, datetime


class SocialService:
    """Service for duets, collaborative videos, live streaming, watch parties, and DMs."""

    def __init__(self, repository):
        self.repository = repository

    # Duet operations
    async def create_duet(
        self,
        original_video_id: str,
        response_video_id: str,
        creator_id: str,
        duet_type: str = "duet",
    ) -> Dict[str, Any]:
        """Create a duet, reaction, or stitch video."""
        from ...infrastructure.repositories.models import DuetDB

        duet = DuetDB(
            original_video_id=original_video_id,
            response_video_id=response_video_id,
            creator_id=creator_id,
            duet_type=duet_type,
        )
        saved = self.repository.save_duet(duet)
        return {"success": True, "duet": saved}

    async def get_duets_for_video(self, video_id: str) -> List[Dict[str, Any]]:
        """Get all duets/reactions/stitches for a video."""
        return self.repository.get_duets_by_video(video_id)

    # Collaborative video operations
    async def create_collaborative_video(
        self, video_id: str, host_id: str, max_participants: int = 4
    ) -> Dict[str, Any]:
        """Create a collaborative multi-creator video session."""
        from ...infrastructure.repositories.models import (
            CollaborativeVideoDB,
            VideoCollaboratorDB,
        )

        collab = CollaborativeVideoDB(
            video_id=video_id,
            status="draft",
            max_participants=max_participants,
        )
        saved = self.repository.save_collaborative_video(collab)

        # Add the host as the first collaborator
        host_collaborator = VideoCollaboratorDB(
            collaborative_video_id=saved.id,
            user_id=host_id,
            role="host",
        )
        self.repository.save_video_collaborator(host_collaborator)

        return {"success": True, "collaborative_video": saved}

    async def join_collaborative_video(
        self, collab_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Join a collaborative video session as a participant."""
        from ...infrastructure.repositories.models import VideoCollaboratorDB

        collab = self.repository.get_collaborative_video(collab_id)
        if not collab:
            return {"success": False, "error": "Collaborative video not found"}

        # Check participant limit
        current_participants = self.repository.get_video_collaborators(collab_id)
        if len(current_participants) >= collab.max_participants:
            return {"success": False, "error": "Maximum participants reached"}

        collaborator = VideoCollaboratorDB(
            collaborative_video_id=collab_id,
            user_id=user_id,
            role="participant",
        )
        saved = self.repository.save_video_collaborator(collaborator)
        return {"success": True, "collaborator": saved}

    # Live streaming operations
    async def start_live_stream(
        self,
        creator_id: str,
        title: str,
        description: str = "",
        scheduled_for: datetime = None,
    ) -> Dict[str, Any]:
        """Start or schedule a live stream."""
        from ...infrastructure.repositories.models import LiveStreamDB

        if scheduled_for:
            status = "scheduled"
            started_at = None
        else:
            status = "live"
            started_at = datetime.now(UTC)

        stream = LiveStreamDB(
            creator_id=creator_id,
            title=title,
            description=description,
            status=status,
            started_at=started_at,
            scheduled_for=scheduled_for,
        )
        saved = self.repository.save_live_stream(stream)
        return {"success": True, "stream": saved}

    async def end_live_stream(
        self, stream_id: str, creator_id: str
    ) -> Dict[str, Any]:
        """End a live stream."""
        stream = self.repository.get_live_stream(stream_id)
        if not stream:
            return {"success": False, "error": "Stream not found"}
        if stream.creator_id != creator_id:
            return {"success": False, "error": "Only the creator can end this stream"}
        if stream.status == "ended":
            return {"success": False, "error": "Stream has already ended"}

        self.repository.update_live_stream_status(
            stream_id, status="ended", ended_at=datetime.now(UTC)
        )
        return {"success": True}

    async def join_live_stream_as_guest(
        self, stream_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Join a live stream as a guest."""
        from ...infrastructure.repositories.models import LiveStreamGuestDB

        stream = self.repository.get_live_stream(stream_id)
        if not stream:
            return {"success": False, "error": "Stream not found"}
        if stream.status != "live":
            return {"success": False, "error": "Stream is not currently live"}

        guest = LiveStreamGuestDB(
            stream_id=stream_id,
            user_id=user_id,
            status="joined",
            joined_at=datetime.now(UTC),
        )
        saved = self.repository.save_live_stream_guest(guest)
        return {"success": True, "guest": saved}

    # Watch party operations
    async def create_watch_party(
        self, host_id: str, video_id: str, title: str
    ) -> Dict[str, Any]:
        """Create a synchronized watch party."""
        from ...infrastructure.repositories.models import WatchPartyDB

        party = WatchPartyDB(
            host_id=host_id,
            video_id=video_id,
            title=title,
            status="waiting",
        )
        saved = self.repository.save_watch_party(party)
        return {"success": True, "watch_party": saved}

    async def join_watch_party(
        self, party_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Join an existing watch party."""
        from ...infrastructure.repositories.models import WatchPartyParticipantDB

        party = self.repository.get_watch_party(party_id)
        if not party:
            return {"success": False, "error": "Watch party not found"}
        if party.status == "ended":
            return {"success": False, "error": "Watch party has ended"}

        participant = WatchPartyParticipantDB(
            party_id=party_id,
            user_id=user_id,
        )
        saved = self.repository.save_watch_party_participant(participant)
        self.repository.increment_watch_party_participant_count(party_id)
        return {"success": True, "participant": saved}

    # Direct messaging operations
    async def send_message(
        self, sender_id: str, receiver_id: str, content: str
    ) -> Dict[str, Any]:
        """Send a direct message to another user."""
        from ...infrastructure.repositories.models import DirectMessageDB

        message = DirectMessageDB(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            is_encrypted=True,
        )
        saved = self.repository.save_direct_message(message)

        # Create or update the conversation
        conversation = self.repository.get_conversation(sender_id, receiver_id)
        if conversation:
            self.repository.update_conversation_last_message(
                conversation.id, datetime.now(UTC)
            )
        else:
            from ...infrastructure.repositories.models import ConversationDB

            conversation = ConversationDB(
                participant_1_id=sender_id,
                participant_2_id=receiver_id,
                last_message_at=datetime.now(UTC),
            )
            self.repository.save_conversation(conversation)

        return {"success": True, "message": saved}

    async def get_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all conversations for a user."""
        return self.repository.get_user_conversations(user_id)

    async def get_messages(
        self, conversation_id: str, user_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get messages in a conversation."""
        conversation = self.repository.get_conversation_by_id(conversation_id)
        if not conversation:
            return []
        if (
            conversation.participant_1_id != user_id
            and conversation.participant_2_id != user_id
        ):
            return []
        return self.repository.get_conversation_messages(conversation_id, limit)
