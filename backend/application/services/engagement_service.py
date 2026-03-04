from typing import List, Optional, Dict, Any
from datetime import datetime


class EngagementService:
    """Service for polls, chapters, product tags, video links, challenges, and badges."""

    def __init__(self, repository):
        self.repository = repository

    # Poll operations
    async def create_poll(
        self,
        video_id: str,
        creator_id: str,
        question: str,
        options: List[str],
        poll_type: str = "poll",
        correct_answer: str = None,
        start_time: float = 0.0,
        end_time: float = 0.0,
    ) -> Dict[str, Any]:
        """Create an in-video poll or quiz."""
        from ...infrastructure.repositories.models import PollDB, PollOptionDB

        poll = PollDB(
            video_id=video_id,
            creator_id=creator_id,
            question=question,
            poll_type=poll_type,
            correct_answer=correct_answer,
            start_time=start_time,
            end_time=end_time,
        )
        saved_poll = self.repository.save_poll(poll)

        saved_options = []
        for option_text in options:
            is_correct = (
                poll_type == "quiz" and option_text == correct_answer
            )
            option = PollOptionDB(
                poll_id=saved_poll.id,
                text=option_text,
                is_correct=is_correct,
            )
            saved_option = self.repository.save_poll_option(option)
            saved_options.append(saved_option)

        return {
            "success": True,
            "poll": saved_poll,
            "options": saved_options,
        }

    async def vote_on_poll(
        self, poll_id: str, option_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Cast a vote on a poll option."""
        from ...infrastructure.repositories.models import PollVoteDB

        # Check if user already voted
        existing_vote = self.repository.get_poll_vote(poll_id, user_id)
        if existing_vote:
            return {"success": False, "error": "Already voted on this poll"}

        vote = PollVoteDB(
            poll_id=poll_id,
            option_id=option_id,
            user_id=user_id,
        )
        saved = self.repository.save_poll_vote(vote)
        self.repository.increment_poll_option_vote_count(option_id)
        self.repository.increment_poll_total_votes(poll_id)
        return {"success": True, "vote": saved}

    async def get_poll(self, poll_id: str) -> Dict[str, Any]:
        """Get a poll with its options and vote counts."""
        poll = self.repository.get_poll(poll_id)
        if not poll:
            return {"success": False, "error": "Poll not found"}
        options = self.repository.get_poll_options(poll_id)
        return {
            "success": True,
            "poll": poll,
            "options": options,
            "total_votes": poll.total_votes,
        }

    async def get_polls_for_video(self, video_id: str) -> List[Dict[str, Any]]:
        """Get all polls associated with a video."""
        return self.repository.get_polls_by_video(video_id)

    # Chapter marker operations
    async def create_chapter_marker(
        self,
        video_id: str,
        title: str,
        start_time: float,
        end_time: float,
        thumbnail_url: str = None,
    ) -> Dict[str, Any]:
        """Create a chapter marker for video navigation."""
        from ...infrastructure.repositories.models import ChapterMarkerDB

        marker = ChapterMarkerDB(
            video_id=video_id,
            title=title,
            start_time=start_time,
            end_time=end_time,
            thumbnail_url=thumbnail_url,
        )
        saved = self.repository.save_chapter_marker(marker)
        return {"success": True, "chapter_marker": saved}

    async def get_chapter_markers(self, video_id: str) -> List[Dict[str, Any]]:
        """Get chapter markers for a video, sorted by start time."""
        return self.repository.get_chapter_markers_by_video(video_id)

    # Product tag operations
    async def add_product_tag(
        self,
        video_id: str,
        creator_id: str,
        product_name: str,
        product_url: str,
        price: float,
        currency: str = "USD",
        position_x: float = 0.0,
        position_y: float = 0.0,
        start_time: float = 0.0,
        end_time: float = 0.0,
        product_image_url: str = None,
    ) -> Dict[str, Any]:
        """Add a shoppable product tag to a video."""
        from ...infrastructure.repositories.models import ProductTagDB

        tag = ProductTagDB(
            video_id=video_id,
            creator_id=creator_id,
            product_name=product_name,
            product_url=product_url,
            price=price,
            currency=currency,
            position_x=position_x,
            position_y=position_y,
            start_time=start_time,
            end_time=end_time,
            product_image_url=product_image_url,
        )
        saved = self.repository.save_product_tag(tag)
        return {"success": True, "product_tag": saved}

    async def get_product_tags(self, video_id: str) -> List[Dict[str, Any]]:
        """Get all product tags for a video."""
        return self.repository.get_product_tags_by_video(video_id)

    async def track_product_click(self, tag_id: str) -> Dict[str, Any]:
        """Track a click on a product tag."""
        self.repository.increment_product_tag_click_count(tag_id)
        return {"success": True}

    # Video link operations
    async def add_video_link(
        self,
        video_id: str,
        creator_id: str,
        title: str,
        url: str,
        icon: str = None,
        position: int = 0,
    ) -> Dict[str, Any]:
        """Add a link-in-bio style link to a video."""
        from ...infrastructure.repositories.models import VideoLinkDB

        link = VideoLinkDB(
            video_id=video_id,
            creator_id=creator_id,
            title=title,
            url=url,
            icon=icon,
            position=position,
        )
        saved = self.repository.save_video_link(link)
        return {"success": True, "video_link": saved}

    async def get_video_links(self, video_id: str) -> List[Dict[str, Any]]:
        """Get all links for a video."""
        return self.repository.get_video_links_by_video(video_id)

    async def track_link_click(self, link_id: str) -> Dict[str, Any]:
        """Track a click on a video link."""
        self.repository.increment_video_link_click_count(link_id)
        return {"success": True}

    # Challenge operations
    async def create_challenge(
        self,
        hashtag_id: str,
        creator_id: str,
        title: str,
        description: str = "",
        rules: str = "",
        start_date: datetime = None,
        end_date: datetime = None,
        prize_description: str = None,
    ) -> Dict[str, Any]:
        """Create a hashtag challenge."""
        from ...infrastructure.repositories.models import ChallengeDB

        status = "upcoming"
        now = datetime.utcnow()
        if start_date and start_date <= now:
            status = "active"

        challenge = ChallengeDB(
            hashtag_id=hashtag_id,
            creator_id=creator_id,
            title=title,
            description=description,
            rules=rules,
            start_date=start_date,
            end_date=end_date,
            prize_description=prize_description,
            status=status,
        )
        saved = self.repository.save_challenge(challenge)
        return {"success": True, "challenge": saved}

    async def join_challenge(
        self, challenge_id: str, user_id: str, video_id: str
    ) -> Dict[str, Any]:
        """Join a challenge by submitting a video."""
        from ...infrastructure.repositories.models import ChallengeParticipantDB

        challenge = self.repository.get_challenge(challenge_id)
        if not challenge:
            return {"success": False, "error": "Challenge not found"}
        if challenge.status != "active":
            return {"success": False, "error": "Challenge is not currently active"}

        participant = ChallengeParticipantDB(
            challenge_id=challenge_id,
            user_id=user_id,
            video_id=video_id,
        )
        saved = self.repository.save_challenge_participant(participant)
        self.repository.increment_challenge_participant_count(challenge_id)
        return {"success": True, "participant": saved}

    async def get_active_challenges(
        self, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get currently active challenges."""
        return self.repository.get_active_challenges(limit)

    # Badge operations
    async def award_badge(
        self, user_id: str, badge_id: str
    ) -> Dict[str, Any]:
        """Award a badge to a user."""
        from ...infrastructure.repositories.models import UserBadgeDB

        # Check if user already has this badge
        existing = self.repository.get_user_badge(user_id, badge_id)
        if existing:
            return {"success": False, "error": "User already has this badge"}

        user_badge = UserBadgeDB(
            user_id=user_id,
            badge_id=badge_id,
        )
        saved = self.repository.save_user_badge(user_badge)
        return {"success": True, "user_badge": saved}

    async def get_user_badges(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all badges earned by a user."""
        return self.repository.get_user_badges(user_id)

    async def check_and_award_supporter_badges(
        self, user_id: str, creator_id: str, total_tips: float
    ) -> Dict[str, Any]:
        """Auto-award supporter badges based on tipping thresholds."""
        thresholds = [
            (10.0, "bronze_supporter"),
            (50.0, "silver_supporter"),
            (100.0, "gold_supporter"),
            (500.0, "platinum_supporter"),
        ]

        awarded = []
        for threshold, badge_type in thresholds:
            if total_tips >= threshold:
                badge = self.repository.get_badge_by_type(badge_type)
                if badge:
                    existing = self.repository.get_user_badge(user_id, badge.id)
                    if not existing:
                        result = await self.award_badge(user_id, badge.id)
                        if result.get("success"):
                            awarded.append(badge_type)

        return {"success": True, "awarded_badges": awarded}
