from typing import List, Optional, Dict, Any
from datetime import datetime
from collections import defaultdict


class DiscoveryService:
    """Service for playlists, preferences, favorites, traffic, retention, and posting times."""

    def __init__(self, repository):
        self.repository = repository

    # Playlist operations
    async def create_playlist(
        self,
        creator_id: str,
        title: str,
        description: str = "",
        is_collaborative: bool = False,
        is_public: bool = True,
    ) -> Dict[str, Any]:
        """Create a new playlist."""
        from ...infrastructure.repositories.models import PlaylistDB

        playlist = PlaylistDB(
            creator_id=creator_id,
            title=title,
            description=description,
            is_collaborative=is_collaborative,
            is_public=is_public,
        )
        saved = self.repository.save_playlist(playlist)
        return {"success": True, "playlist": saved}

    async def add_to_playlist(
        self, playlist_id: str, video_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Add a video to a playlist."""
        from ...infrastructure.repositories.models import PlaylistItemDB

        playlist = self.repository.get_playlist(playlist_id)
        if not playlist:
            return {"success": False, "error": "Playlist not found"}

        # Validate access: owner or collaborator on a collaborative playlist
        if playlist.creator_id != user_id:
            if not playlist.is_collaborative:
                return {"success": False, "error": "Access denied"}
            collaborator = self.repository.get_playlist_collaborator(
                playlist_id, user_id
            )
            if not collaborator:
                return {"success": False, "error": "Access denied"}

        # Determine position (append to end)
        current_items = self.repository.get_playlist_items(playlist_id)
        position = len(current_items)

        item = PlaylistItemDB(
            playlist_id=playlist_id,
            video_id=video_id,
            position=position,
            added_by=user_id,
        )
        saved = self.repository.save_playlist_item(item)
        return {"success": True, "playlist_item": saved}

    async def remove_from_playlist(
        self, playlist_id: str, video_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Remove a video from a playlist."""
        playlist = self.repository.get_playlist(playlist_id)
        if not playlist:
            return {"success": False, "error": "Playlist not found"}
        if playlist.creator_id != user_id:
            return {"success": False, "error": "Access denied"}

        self.repository.remove_playlist_item(playlist_id, video_id)
        return {"success": True}

    async def add_playlist_collaborator(
        self, playlist_id: str, user_id: str, owner_id: str
    ) -> Dict[str, Any]:
        """Add a collaborator to a playlist."""
        from ...infrastructure.repositories.models import PlaylistCollaboratorDB

        playlist = self.repository.get_playlist(playlist_id)
        if not playlist:
            return {"success": False, "error": "Playlist not found"}
        if playlist.creator_id != owner_id:
            return {"success": False, "error": "Only the owner can add collaborators"}
        if not playlist.is_collaborative:
            return {"success": False, "error": "Playlist is not collaborative"}

        collaborator = PlaylistCollaboratorDB(
            playlist_id=playlist_id,
            user_id=user_id,
        )
        saved = self.repository.save_playlist_collaborator(collaborator)
        return {"success": True, "collaborator": saved}

    async def get_playlist(self, playlist_id: str) -> Dict[str, Any]:
        """Get a playlist with its items."""
        playlist = self.repository.get_playlist(playlist_id)
        if not playlist:
            return {"success": False, "error": "Playlist not found"}
        items = self.repository.get_playlist_items(playlist_id)
        return {"success": True, "playlist": playlist, "items": items}

    async def get_user_playlists(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all playlists created by a user."""
        return self.repository.get_playlists_by_user(user_id)

    # User preferences operations
    async def update_user_preferences(
        self, user_id: str, preferences_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create or update user feed preferences."""
        from ...infrastructure.repositories.models import UserPreferencesDB

        existing = self.repository.get_user_preferences(user_id)
        if existing:
            self.repository.update_user_preferences(user_id, preferences_data)
            updated = self.repository.get_user_preferences(user_id)
            return {"success": True, "preferences": updated}

        import json

        preferences = UserPreferencesDB(
            user_id=user_id,
            interest_weight=preferences_data.get("interest_weight", 1.0),
            community_weight=preferences_data.get("community_weight", 1.0),
            virality_weight=preferences_data.get("virality_weight", 1.0),
            freshness_weight=preferences_data.get("freshness_weight", 1.0),
            preferred_categories=json.dumps(
                preferences_data.get("preferred_categories", [])
            ),
            preferred_languages=json.dumps(
                preferences_data.get("preferred_languages", [])
            ),
            location=preferences_data.get("location"),
        )
        saved = self.repository.save_user_preferences(preferences)
        return {"success": True, "preferences": saved}

    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences, returning defaults if none set."""
        preferences = self.repository.get_user_preferences(user_id)
        if preferences:
            return {"success": True, "preferences": preferences}
        return {
            "success": True,
            "preferences": {
                "interest_weight": 1.0,
                "community_weight": 1.0,
                "virality_weight": 1.0,
                "freshness_weight": 1.0,
                "preferred_categories": [],
                "preferred_languages": [],
                "location": None,
            },
        }

    # Favorite creator operations
    async def add_favorite_creator(
        self, user_id: str, creator_id: str, priority_notifications: bool = True
    ) -> Dict[str, Any]:
        """Add a creator to favorites with priority notification support."""
        from ...infrastructure.repositories.models import FavoriteCreatorDB

        existing = self.repository.get_favorite_creator(user_id, creator_id)
        if existing:
            return {"success": False, "error": "Creator is already a favorite"}

        favorite = FavoriteCreatorDB(
            user_id=user_id,
            creator_id=creator_id,
            priority_notifications=priority_notifications,
        )
        saved = self.repository.save_favorite_creator(favorite)
        return {"success": True, "favorite": saved}

    async def remove_favorite_creator(
        self, user_id: str, creator_id: str
    ) -> Dict[str, Any]:
        """Remove a creator from favorites."""
        self.repository.delete_favorite_creator(user_id, creator_id)
        return {"success": True}

    async def get_favorite_creators(self, user_id: str) -> List[Dict[str, Any]]:
        """Get a user's favorite creators."""
        return self.repository.get_favorite_creators(user_id)

    # Discovery score
    async def calculate_discovery_score(
        self, video_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Calculate a discovery score explaining why a video was recommended."""
        preferences = self.repository.get_user_preferences(user_id)

        interest_weight = preferences.interest_weight if preferences else 1.0
        community_weight = preferences.community_weight if preferences else 1.0
        virality_weight = preferences.virality_weight if preferences else 1.0
        freshness_weight = preferences.freshness_weight if preferences else 1.0

        # Calculate component scores (0.0 to 1.0)
        interest_score = self.repository.calculate_interest_score(video_id, user_id)
        community_score = self.repository.calculate_community_score(video_id, user_id)
        virality_score = self.repository.calculate_virality_score(video_id)
        freshness_score = self.repository.calculate_freshness_score(video_id)

        # Weighted total
        total_weight = (
            interest_weight + community_weight + virality_weight + freshness_weight
        )
        if total_weight == 0:
            total_weight = 1.0

        final_score = (
            interest_score * interest_weight
            + community_score * community_weight
            + virality_score * virality_weight
            + freshness_score * freshness_weight
        ) / total_weight

        return {
            "success": True,
            "score": final_score,
            "breakdown": {
                "interest": {
                    "score": interest_score,
                    "weight": interest_weight,
                },
                "community": {
                    "score": community_score,
                    "weight": community_weight,
                },
                "virality": {
                    "score": virality_score,
                    "weight": virality_weight,
                },
                "freshness": {
                    "score": freshness_score,
                    "weight": freshness_weight,
                },
            },
        }

    # Traffic source operations
    async def track_traffic_source(
        self,
        video_id: str,
        user_id: str,
        source_type: str,
        referrer_url: str = None,
    ) -> Dict[str, Any]:
        """Track the traffic source for a video view."""
        from ...infrastructure.repositories.models import TrafficSourceDB

        source = TrafficSourceDB(
            video_id=video_id,
            user_id=user_id,
            source_type=source_type,
            referrer_url=referrer_url,
        )
        saved = self.repository.save_traffic_source(source)
        return {"success": True, "traffic_source": saved}

    async def get_traffic_breakdown(self, video_id: str) -> Dict[str, Any]:
        """Get aggregated traffic source percentages for a video."""
        sources = self.repository.get_traffic_sources(video_id)
        total = len(sources) if sources else 0
        if total == 0:
            return {"success": True, "breakdown": {}, "total_views": 0}

        counts = defaultdict(int)
        for source in sources:
            counts[source.source_type] += 1

        breakdown = {
            source_type: round(count / total * 100, 2)
            for source_type, count in counts.items()
        }

        return {"success": True, "breakdown": breakdown, "total_views": total}

    # Retention tracking operations
    async def track_retention(
        self,
        video_id: str,
        second_offset: int,
        viewer_count: int,
        drop_off_count: int,
    ) -> Dict[str, Any]:
        """Track retention data at a specific second in a video."""
        from ...infrastructure.repositories.models import RetentionDataDB

        retention = RetentionDataDB(
            video_id=video_id,
            second_offset=second_offset,
            viewer_count=viewer_count,
            drop_off_count=drop_off_count,
        )
        saved = self.repository.save_retention_data(retention)
        return {"success": True, "retention_data": saved}

    async def get_retention_graph(self, video_id: str) -> Dict[str, Any]:
        """Get retention data points for graphing."""
        data_points = self.repository.get_retention_data(video_id)
        return {"success": True, "data_points": data_points}

    # Posting time recommendations
    async def calculate_best_posting_times(
        self, user_id: str
    ) -> Dict[str, Any]:
        """Analyze video performance to recommend best posting times."""
        from ...infrastructure.repositories.models import PostingTimeRecommendationDB

        # Get user's video performance data grouped by posting day/hour
        performance_data = self.repository.get_video_performance_by_time(user_id)

        recommendations = []
        for day_hour, metrics in performance_data.items():
            day, hour = day_hour
            engagement_score = metrics.get("avg_engagement", 0.0)
            sample_size = metrics.get("sample_size", 0)

            recommendation = PostingTimeRecommendationDB(
                user_id=user_id,
                day_of_week=day,
                hour=hour,
                engagement_score=engagement_score,
                sample_size=sample_size,
            )
            saved = self.repository.save_posting_recommendation(recommendation)
            recommendations.append(saved)

        # Sort by engagement score and return top 5
        recommendations.sort(
            key=lambda r: r.engagement_score, reverse=True
        )
        top_5 = recommendations[:5]

        return {"success": True, "recommendations": top_5}

    async def get_posting_recommendations(
        self, user_id: str
    ) -> Dict[str, Any]:
        """Get saved posting time recommendations for a user."""
        recommendations = self.repository.get_posting_recommendations(user_id)
        return {"success": True, "recommendations": recommendations}
