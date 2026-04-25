from typing import List, Optional, Set
from datetime import datetime
from ...domain.ports.repository_ports import (
    FollowRepositoryPort,
    VideoRepositoryPort,
    InteractionRepositoryPort,
    UserRepositoryPort,
)
from ...domain.ports.user_block_port import UserBlockRepositoryPort
from ...domain.entities.video import Video
from ..services.recommendation_engine import RecommendationEngine


class GetPersonalizedFeedUseCase:
    """Use case for generating personalized video feeds."""

    def __init__(
        self,
        video_repo: VideoRepositoryPort,
        interaction_repo: InteractionRepositoryPort,
        user_repo: UserRepositoryPort,
        user_block_repo: Optional[UserBlockRepositoryPort] = None,
        follow_repo: Optional[FollowRepositoryPort] = None,
    ):
        self.video_repo = video_repo
        self.interaction_repo = interaction_repo
        self.user_repo = user_repo
        self.user_block_repo = user_block_repo
        self.follow_repo = follow_repo
        self.recommendation_engine = RecommendationEngine()

    def _blocked_creator_ids(self, viewer_id: str) -> Set[str]:
        """Creator IDs the viewer has blocked plus those who have blocked the viewer."""
        if self.user_block_repo is None:
            return set()
        blocked = set(self.user_block_repo.list_blocked_ids(viewer_id))
        # Also hide content from users who blocked us — Apple Guideline 1.2
        blocked.update(self.user_block_repo.list_blockers_of(viewer_id))
        return blocked

    def execute(
        self,
        user_id: str,
        feed_type: str = "foryou",  # "foryou", "following", "trending"
        page: int = 1,
        page_size: int = 20,
    ) -> List[Video]:
        """
        Generate personalized feed based on feed type.

        Args:
            user_id: Current user ID
            feed_type: Type of feed ("foryou", "following", "trending")
            page: Page number for pagination
            page_size: Number of videos per page

        Returns:
            List of Video objects
        """

        # Get user's following list
        user_following = self._get_user_following(user_id)

        if feed_type == "following":
            # Optimized path: only fetch videos from followed creators
            feed_videos = self.video_repo.get_videos_from_creators(
                creator_ids=list(user_following),
                offset=(page - 1) * page_size,
                limit=page_size,
            )
        else:
            # Load shared data once for recommendation-based feeds.
            # Some legacy interaction-repo methods may not exist on every
            # implementation — fall back to empty lists for the recommender.
            _get_user = getattr(self.interaction_repo, "get_user_interactions", None)
            _get_all = getattr(self.interaction_repo, "get_all_interactions", None)
            user_interactions = _get_user(user_id) if _get_user else []
            all_videos = self.video_repo.find_all(offset=0, limit=500)
            all_interactions = _get_all(limit=5000) if _get_all else []

            if feed_type == "trending":
                feed_videos = self.recommendation_engine.get_trending_videos(
                    all_videos=all_videos,
                    all_interactions=all_interactions,
                    hours=24,
                )
            else:
                # "foryou" or unknown feed type
                feed_videos = self.recommendation_engine.get_for_you_feed(
                    user_id=user_id,
                    user_interactions=user_interactions,
                    all_videos=all_videos,
                    all_interactions=all_interactions,
                    user_following=user_following,
                    include_trending=(feed_type == "foryou"),
                )

        # Filter out blocked users (both directions). Apple Guideline 1.2.
        blocked = self._blocked_creator_ids(user_id)
        if blocked:
            feed_videos = [v for v in feed_videos if v.creator_id not in blocked]

        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        return feed_videos[start_idx:end_idx]

    def get_feed_count(self, user_id: str, feed_type: str = "foryou") -> int:
        """Get total count of videos in feed type."""

        if feed_type == "following":
            user_following = self._get_user_following(user_id)
            return self.video_repo.count_videos_from_creators(list(user_following))

        elif feed_type == "trending":
            return 50  # Trending feed is capped at 50

        # For "foryou" feed, we return a reasonable limit
        return 50  # We limit to 50 recommendations per user

    def _get_user_following(self, user_id: str) -> Set[str]:
        """Get set of creator IDs that user follows.

        Prefer FollowRepositoryPort (canonical source of follow edges).
        Fall back to interaction-style following if a repo isn't injected.
        """
        if self.follow_repo is not None:
            return {f.followed_id for f in self.follow_repo.get_following(user_id)}
        following = getattr(self.interaction_repo, "get_user_following", None)
        if not following:
            return set()
        return {i.target_user_id for i in following(user_id)}
