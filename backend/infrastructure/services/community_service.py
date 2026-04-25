from typing import List, Optional, Dict, Any
from datetime import datetime


class CommunityService:
    """Service for community groups, circles, events, and discussions."""

    def __init__(self, repository):
        self.repository = repository

    # Circle operations
    async def create_circle(
        self, user_id: str, name: str, description: str = ""
    ) -> Dict[str, Any]:
        """Create a new circle for organizing followed creators."""
        from ...infrastructure.repositories.models import CircleDB

        circle = CircleDB(user_id=user_id, name=name, description=description)
        saved = self.repository.save_circle(circle)
        return {"success": True, "circle": saved}

    async def add_to_circle(
        self, circle_id: str, member_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Add a creator to a circle."""
        circle = self.repository.get_circle(circle_id)
        if not circle or circle.user_id != user_id:
            return {"success": False, "error": "Circle not found or access denied"}
        member = self.repository.add_circle_member(circle_id, member_id)
        return {"success": True, "member": member}

    async def remove_from_circle(
        self, circle_id: str, member_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Remove a creator from a circle."""
        circle = self.repository.get_circle(circle_id)
        if not circle or circle.user_id != user_id:
            return {"success": False, "error": "Circle not found or access denied"}
        self.repository.remove_circle_member(circle_id, member_id)
        return {"success": True}

    async def get_user_circles(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all circles belonging to a user."""
        return self.repository.get_circles_by_user(user_id)

    async def get_circle_members(
        self, circle_id: str, user_id: str
    ) -> List[Dict[str, Any]]:
        """Get all members in a circle, if the user owns it."""
        circle = self.repository.get_circle(circle_id)
        if not circle or circle.user_id != user_id:
            return []
        return self.repository.get_circle_members(circle_id)

    # Community Group operations
    async def create_group(
        self,
        creator_id: str,
        name: str,
        description: str = "",
        rules: str = "",
        is_public: bool = True,
    ) -> Dict[str, Any]:
        """Create a new community group."""
        from ...infrastructure.repositories.models import CommunityGroupDB

        group = CommunityGroupDB(
            creator_id=creator_id,
            name=name,
            description=description,
            rules=rules,
            is_public=is_public,
        )
        saved = self.repository.save_group(group)
        return {"success": True, "group": saved}

    async def join_group(self, group_id: str, user_id: str) -> Dict[str, Any]:
        """Join a community group."""
        group = self.repository.get_group(group_id)
        if not group:
            return {"success": False, "error": "Group not found"}
        if not group.is_public:
            return {"success": False, "error": "Group is private"}
        member = self.repository.add_group_member(group_id, user_id, role="member")
        self.repository.increment_group_member_count(group_id)
        return {"success": True, "member": member}

    async def leave_group(self, group_id: str, user_id: str) -> Dict[str, Any]:
        """Leave a community group."""
        self.repository.remove_group_member(group_id, user_id)
        self.repository.decrement_group_member_count(group_id)
        return {"success": True}

    async def get_group(self, group_id: str) -> Optional[Dict[str, Any]]:
        """Get a community group by ID."""
        return self.repository.get_group(group_id)

    async def list_groups(
        self, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List public community groups."""
        return self.repository.list_public_groups(limit, offset)

    # Discussion operations
    async def create_discussion_post(
        self,
        group_id: str,
        user_id: str,
        content: str,
        parent_id: str = None,
    ) -> Dict[str, Any]:
        """Create a discussion post in a community group."""
        member = self.repository.get_group_member(group_id, user_id)
        if not member:
            return {"success": False, "error": "Must be a group member to post"}
        from ...infrastructure.repositories.models import DiscussionPostDB

        post = DiscussionPostDB(
            group_id=group_id,
            user_id=user_id,
            content=content,
            parent_id=parent_id,
        )
        saved = self.repository.save_discussion_post(post)
        return {"success": True, "post": saved}

    async def get_discussion_posts(
        self, group_id: str, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get discussion posts for a community group."""
        return self.repository.get_discussion_posts(group_id, limit, offset)

    # Event operations
    async def create_event(
        self,
        creator_id: str,
        title: str,
        description: str = "",
        event_type: str = "online",
        start_time: datetime = None,
        end_time: datetime = None,
        location: str = None,
        max_attendees: int = 0,
        group_id: str = None,
    ) -> Dict[str, Any]:
        """Create a new event (online, in-person, or hybrid)."""
        from ...infrastructure.repositories.models import EventDB

        event = EventDB(
            creator_id=creator_id,
            title=title,
            description=description,
            event_type=event_type,
            start_time=start_time,
            end_time=end_time,
            location=location,
            max_attendees=max_attendees,
            group_id=group_id,
            status="upcoming",
        )
        saved = self.repository.save_event(event)
        return {"success": True, "event": saved}

    async def rsvp_event(
        self, event_id: str, user_id: str, rsvp_status: str = "going"
    ) -> Dict[str, Any]:
        """RSVP to an event."""
        event = self.repository.get_event(event_id)
        if not event:
            return {"success": False, "error": "Event not found"}
        if (
            event.max_attendees > 0
            and event.attendee_count >= event.max_attendees
            and rsvp_status == "going"
        ):
            return {"success": False, "error": "Event is full"}
        attendee = self.repository.upsert_event_attendee(
            event_id, user_id, rsvp_status
        )
        if rsvp_status == "going":
            self.repository.increment_event_attendee_count(event_id)
        return {"success": True, "attendee": attendee}

    async def get_events(
        self, group_id: str = None, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get events, optionally filtered by group."""
        if group_id:
            return self.repository.get_events_by_group(group_id, limit)
        return self.repository.get_upcoming_events(limit)
