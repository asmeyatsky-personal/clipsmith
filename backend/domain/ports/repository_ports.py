from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Dict
from ..entities.video import Video
from ..entities.user import User
from ..entities.caption import Caption  # Import Caption entity
from ..entities.tip import Tip  # Import Tip entity
from ..entities.follow import Follow  # Import Follow entity
from ..entities.notification import Notification, NotificationStatus
from ..entities.hashtag import Hashtag
from ..entities.content_moderation import (
    ContentModeration,
    ModerationStatus,
    ModerationSeverity,
)
from ..entities.video_editor import (
    VideoProject,
    VideoEditorAsset,
    VideoEditorTransition,
    VideoEditorTrack,
    VideoEditorCaption,
    VideoProjectStatus,
)
from ..entities.community import (
    Circle,
    CircleMember,
    CommunityGroup,
    CommunityMember,
    DiscussionPost,
    Event,
    EventAttendee,
)
from ..entities.social import (
    Duet,
    CollaborativeVideo,
    VideoCollaborator,
    LiveStream,
    LiveStreamGuest,
    WatchParty,
    WatchPartyParticipant,
    DirectMessage,
    Conversation,
)
from ..entities.engagement import (
    Poll,
    PollOption,
    PollVote,
    ChapterMarker,
    ProductTag,
    VideoLink,
    Challenge,
    ChallengeParticipant,
    Badge,
    UserBadge,
)
from ..entities.discovery import (
    Playlist,
    PlaylistItem,
    PlaylistCollaborator,
    UserPreferences,
    FavoriteCreator,
    TrafficSource,
    RetentionData,
    PostingTimeRecommendation,
)
from ..entities.course import (
    Course,
    CourseLesson,
    CourseEnrollment,
    SubscriptionTier,
    CreatorFundEligibility,
)


class VideoRepositoryPort(ABC):
    @abstractmethod
    def save(self, video: Video) -> Video:
        pass

    @abstractmethod
    def get_by_id(self, video_id: str) -> Optional[Video]:
        pass

    @abstractmethod
    def find_all(self, offset: int = 0, limit: int = 20) -> List[Video]:
        pass

    @abstractmethod
    def count_all(self) -> int:
        pass

    @abstractmethod
    def list_by_creator(self, creator_id: str) -> List[Video]:
        pass

    @abstractmethod
    def delete(self, video_id: str) -> bool:
        pass

    @abstractmethod
    def increment_views(self, video_id: str) -> Optional[Video]:
        pass

    @abstractmethod
    def search(self, query: str, offset: int = 0, limit: int = 20) -> List[Video]:
        pass

    @abstractmethod
    def count_search(self, query: str) -> int:
        pass


class InteractionRepositoryPort(ABC):
    @abstractmethod
    def toggle_like(self, user_id: str, video_id: str) -> bool:
        pass

    @abstractmethod
    def has_user_liked(self, user_id: str, video_id: str) -> bool:
        pass

    @abstractmethod
    def add_comment(self, user_id: str, username: str, video_id: str, content: str):
        pass

    @abstractmethod
    def list_comments(self, video_id: str) -> List:
        pass

    def get_user_interactions(self, user_id: str) -> List:
        return []

    def get_all_interactions(self, limit: int = 5000) -> List:
        return []

    def get_user_following(self, user_id: str) -> List:
        return []


class UserRepositoryPort(ABC):
    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        pass


class CaptionRepositoryPort(ABC):
    @abstractmethod
    def save(self, caption: Caption) -> Caption:
        pass

    @abstractmethod
    def get_by_video_id(self, video_id: str) -> List[Caption]:
        pass

    @abstractmethod
    def delete_by_video_id(self, video_id: str) -> bool:
        pass


class TipRepositoryPort(ABC):
    @abstractmethod
    def save(self, tip: Tip) -> Tip:
        pass

    @abstractmethod
    def get_tips_by_receiver_id(self, receiver_id: str) -> List[Tip]:
        pass

    @abstractmethod
    def get_tips_by_sender_id(self, sender_id: str) -> List[Tip]:
        pass

    @abstractmethod
    def get_tips_by_video_id(self, video_id: str) -> List[Tip]:
        pass


class FollowRepositoryPort(ABC):
    @abstractmethod
    def follow(self, follower_id: str, followed_id: str) -> Follow:
        pass

    @abstractmethod
    def unfollow(self, follower_id: str, followed_id: str) -> bool:
        pass


class NotificationRepositoryPort(ABC):
    @abstractmethod
    def save(self, notification: "Notification") -> "Notification":
        pass

    @abstractmethod
    def get_by_id(self, notification_id: str) -> Optional["Notification"]:
        pass

    @abstractmethod
    def get_user_notifications(
        self,
        user_id: str,
        status: Optional["NotificationStatus"] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> List["Notification"]:
        pass

    @abstractmethod
    def count_user_notifications(
        self, user_id: str, status: Optional["NotificationStatus"] = None
    ) -> int:
        pass

    @abstractmethod
    def mark_as_read(self, notification_id: str) -> Optional["Notification"]:
        pass

    @abstractmethod
    def mark_all_as_read(self, user_id: str) -> int:
        pass

    @abstractmethod
    def delete_notification(self, notification_id: str) -> bool:
        pass

    @abstractmethod
    def get_unread_count(self, user_id: str) -> int:
        pass


class HashtagRepositoryPort(ABC):
    @abstractmethod
    def save(self, hashtag: "Hashtag") -> "Hashtag":
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Optional["Hashtag"]:
        pass

    @abstractmethod
    def get_trending_hashtags(self, limit: int = 50) -> List["Hashtag"]:
        pass

    @abstractmethod
    def get_popular_hashtags(self, limit: int = 50) -> List["Hashtag"]:
        pass

    @abstractmethod
    def search_hashtags(self, query: str, limit: int = 20) -> List["Hashtag"]:
        pass

    @abstractmethod
    def update_hashtag_usage(self, hashtag_name: str) -> Optional["Hashtag"]:
        pass

    @abstractmethod
    def update_trending_scores(self, hashtag_scores: dict[str, float]) -> int:
        pass

    @abstractmethod
    def get_recent_hashtags(self, hours: int = 24, limit: int = 20) -> List["Hashtag"]:
        pass


class ContentModerationRepositoryPort(ABC):
    @abstractmethod
    def save(self, moderation: "ContentModeration") -> "ContentModeration":
        pass

    @abstractmethod
    def get_by_id(self, moderation_id: str) -> Optional["ContentModeration"]:
        pass

    @abstractmethod
    def get_pending_moderations(self, limit: int = 50) -> List["ContentModeration"]:
        pass

    @abstractmethod
    def get_moderations_by_content_id(
        self, content_id: str, content_type: Optional[str] = None
    ) -> List["ContentModeration"]:
        pass

    @abstractmethod
    def get_moderations_by_status(
        self, status: "ModerationStatus", limit: int = 100
    ) -> List["ContentModeration"]:
        pass

    @abstractmethod
    def get_moderations_by_reviewer(
        self, reviewer_id: str, limit: int = 100
    ) -> List["ContentModeration"]:
        pass

    @abstractmethod
    def get_flagged_content(
        self, severity: Optional[ModerationSeverity] = None, limit: int = 50
    ) -> List["ContentModeration"]:
        pass

    @abstractmethod
    def get_statistics(self, days: int = 30) -> Dict[str, int]:
        pass

    @abstractmethod
    def delete_old_records(self, days: int = 90) -> int:
        pass


class CommunityRepositoryPort(ABC):
    """Repository port for community features: groups, circles, events, discussions."""

    # Circle operations
    @abstractmethod
    def save_circle(self, circle: Circle) -> Circle:
        """Save or update a circle."""
        pass

    @abstractmethod
    def get_circle_by_id(self, circle_id: str) -> Optional[Circle]:
        """Get circle by ID."""
        pass

    @abstractmethod
    def get_circles_by_user(self, user_id: str) -> List[Circle]:
        """Get all circles owned by a user."""
        pass

    @abstractmethod
    def delete_circle(self, circle_id: str) -> bool:
        """Delete a circle."""
        pass

    @abstractmethod
    def add_circle_member(self, member: CircleMember) -> CircleMember:
        """Add a member to a circle."""
        pass

    @abstractmethod
    def remove_circle_member(self, circle_id: str, member_id: str) -> bool:
        """Remove a member from a circle."""
        pass

    @abstractmethod
    def get_circle_members(self, circle_id: str) -> List[CircleMember]:
        """Get all members of a circle."""
        pass

    # Community group operations
    @abstractmethod
    def save_group(self, group: CommunityGroup) -> CommunityGroup:
        """Save or update a community group."""
        pass

    @abstractmethod
    def get_group_by_id(self, group_id: str) -> Optional[CommunityGroup]:
        """Get community group by ID."""
        pass

    @abstractmethod
    def get_public_groups(self, offset: int = 0, limit: int = 20) -> List[CommunityGroup]:
        """Get public community groups."""
        pass

    @abstractmethod
    def get_groups_by_creator(self, creator_id: str) -> List[CommunityGroup]:
        """Get all groups created by a user."""
        pass

    @abstractmethod
    def delete_group(self, group_id: str) -> bool:
        """Delete a community group."""
        pass

    @abstractmethod
    def add_group_member(self, member: CommunityMember) -> CommunityMember:
        """Add a member to a community group."""
        pass

    @abstractmethod
    def remove_group_member(self, group_id: str, user_id: str) -> bool:
        """Remove a member from a community group."""
        pass

    @abstractmethod
    def get_group_members(self, group_id: str, offset: int = 0, limit: int = 50) -> List[CommunityMember]:
        """Get members of a community group."""
        pass

    @abstractmethod
    def get_user_groups(self, user_id: str) -> List[CommunityGroup]:
        """Get groups a user belongs to."""
        pass

    # Discussion operations
    @abstractmethod
    def save_discussion_post(self, post: DiscussionPost) -> DiscussionPost:
        """Save or update a discussion post."""
        pass

    @abstractmethod
    def get_discussion_post_by_id(self, post_id: str) -> Optional[DiscussionPost]:
        """Get discussion post by ID."""
        pass

    @abstractmethod
    def get_group_discussions(self, group_id: str, offset: int = 0, limit: int = 20) -> List[DiscussionPost]:
        """Get discussion posts for a group."""
        pass

    @abstractmethod
    def get_discussion_replies(self, parent_id: str, offset: int = 0, limit: int = 20) -> List[DiscussionPost]:
        """Get replies to a discussion post."""
        pass

    @abstractmethod
    def delete_discussion_post(self, post_id: str) -> bool:
        """Delete a discussion post."""
        pass

    # Event operations
    @abstractmethod
    def save_event(self, event: Event) -> Event:
        """Save or update an event."""
        pass

    @abstractmethod
    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Get event by ID."""
        pass

    @abstractmethod
    def get_upcoming_events(self, offset: int = 0, limit: int = 20) -> List[Event]:
        """Get upcoming events."""
        pass

    @abstractmethod
    def get_group_events(self, group_id: str, offset: int = 0, limit: int = 20) -> List[Event]:
        """Get events for a specific group."""
        pass

    @abstractmethod
    def delete_event(self, event_id: str) -> bool:
        """Delete an event."""
        pass

    @abstractmethod
    def save_event_attendee(self, attendee: EventAttendee) -> EventAttendee:
        """Save or update an event attendee."""
        pass

    @abstractmethod
    def remove_event_attendee(self, event_id: str, user_id: str) -> bool:
        """Remove an attendee from an event."""
        pass

    @abstractmethod
    def get_event_attendees(self, event_id: str) -> List[EventAttendee]:
        """Get all attendees for an event."""
        pass


class SocialRepositoryPort(ABC):
    """Repository port for social features: duets, collabs, live streams, watch parties, DMs."""

    # Duet operations
    @abstractmethod
    def save_duet(self, duet: Duet) -> Duet:
        """Save or update a duet."""
        pass

    @abstractmethod
    def get_duet_by_id(self, duet_id: str) -> Optional[Duet]:
        """Get duet by ID."""
        pass

    @abstractmethod
    def get_duets_by_video(self, video_id: str) -> List[Duet]:
        """Get all duets for an original video."""
        pass

    @abstractmethod
    def get_duets_by_creator(self, creator_id: str) -> List[Duet]:
        """Get all duets created by a user."""
        pass

    @abstractmethod
    def delete_duet(self, duet_id: str) -> bool:
        """Delete a duet."""
        pass

    # Collaborative video operations
    @abstractmethod
    def save_collaborative_video(self, collab: CollaborativeVideo) -> CollaborativeVideo:
        """Save or update a collaborative video."""
        pass

    @abstractmethod
    def get_collaborative_video_by_id(self, collab_id: str) -> Optional[CollaborativeVideo]:
        """Get collaborative video by ID."""
        pass

    @abstractmethod
    def add_video_collaborator(self, collaborator: VideoCollaborator) -> VideoCollaborator:
        """Add a collaborator to a collaborative video."""
        pass

    @abstractmethod
    def remove_video_collaborator(self, collab_id: str, user_id: str) -> bool:
        """Remove a collaborator from a collaborative video."""
        pass

    @abstractmethod
    def get_video_collaborators(self, collab_id: str) -> List[VideoCollaborator]:
        """Get collaborators for a collaborative video."""
        pass

    # Live stream operations
    @abstractmethod
    def save_live_stream(self, stream: LiveStream) -> LiveStream:
        """Save or update a live stream."""
        pass

    @abstractmethod
    def get_live_stream_by_id(self, stream_id: str) -> Optional[LiveStream]:
        """Get live stream by ID."""
        pass

    @abstractmethod
    def get_active_live_streams(self, offset: int = 0, limit: int = 20) -> List[LiveStream]:
        """Get currently active live streams."""
        pass

    @abstractmethod
    def get_live_streams_by_creator(self, creator_id: str) -> List[LiveStream]:
        """Get all live streams by a creator."""
        pass

    @abstractmethod
    def delete_live_stream(self, stream_id: str) -> bool:
        """Delete a live stream."""
        pass

    @abstractmethod
    def save_live_stream_guest(self, guest: LiveStreamGuest) -> LiveStreamGuest:
        """Save or update a live stream guest."""
        pass

    @abstractmethod
    def get_live_stream_guests(self, stream_id: str) -> List[LiveStreamGuest]:
        """Get guests for a live stream."""
        pass

    # Watch party operations
    @abstractmethod
    def save_watch_party(self, party: WatchParty) -> WatchParty:
        """Save or update a watch party."""
        pass

    @abstractmethod
    def get_watch_party_by_id(self, party_id: str) -> Optional[WatchParty]:
        """Get watch party by ID."""
        pass

    @abstractmethod
    def get_active_watch_parties(self, offset: int = 0, limit: int = 20) -> List[WatchParty]:
        """Get active watch parties."""
        pass

    @abstractmethod
    def delete_watch_party(self, party_id: str) -> bool:
        """Delete a watch party."""
        pass

    @abstractmethod
    def add_watch_party_participant(self, participant: WatchPartyParticipant) -> WatchPartyParticipant:
        """Add a participant to a watch party."""
        pass

    @abstractmethod
    def remove_watch_party_participant(self, party_id: str, user_id: str) -> bool:
        """Remove a participant from a watch party."""
        pass

    @abstractmethod
    def get_watch_party_participants(self, party_id: str) -> List[WatchPartyParticipant]:
        """Get participants of a watch party."""
        pass

    # Direct message operations
    @abstractmethod
    def save_direct_message(self, message: DirectMessage) -> DirectMessage:
        """Save a direct message."""
        pass

    @abstractmethod
    def get_direct_message_by_id(self, message_id: str) -> Optional[DirectMessage]:
        """Get direct message by ID."""
        pass

    @abstractmethod
    def get_conversation_messages(self, conversation_id: str, offset: int = 0, limit: int = 50) -> List[DirectMessage]:
        """Get messages in a conversation."""
        pass

    @abstractmethod
    def mark_message_as_read(self, message_id: str) -> Optional[DirectMessage]:
        """Mark a message as read."""
        pass

    @abstractmethod
    def save_conversation(self, conversation: Conversation) -> Conversation:
        """Save or update a conversation."""
        pass

    @abstractmethod
    def get_conversation_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID."""
        pass

    @abstractmethod
    def get_user_conversations(self, user_id: str, offset: int = 0, limit: int = 20) -> List[Conversation]:
        """Get all conversations for a user."""
        pass

    @abstractmethod
    def get_conversation_between(self, user_id_1: str, user_id_2: str) -> Optional[Conversation]:
        """Get conversation between two users."""
        pass


class EngagementRepositoryPort(ABC):
    """Repository port for engagement tools: polls, chapters, product tags, video links, challenges, badges."""

    # Poll operations
    @abstractmethod
    def save_poll(self, poll: Poll) -> Poll:
        """Save or update a poll."""
        pass

    @abstractmethod
    def get_poll_by_id(self, poll_id: str) -> Optional[Poll]:
        """Get poll by ID."""
        pass

    @abstractmethod
    def get_polls_by_video(self, video_id: str) -> List[Poll]:
        """Get polls for a video."""
        pass

    @abstractmethod
    def delete_poll(self, poll_id: str) -> bool:
        """Delete a poll."""
        pass

    @abstractmethod
    def save_poll_option(self, option: PollOption) -> PollOption:
        """Save or update a poll option."""
        pass

    @abstractmethod
    def get_poll_options(self, poll_id: str) -> List[PollOption]:
        """Get options for a poll."""
        pass

    @abstractmethod
    def save_poll_vote(self, vote: PollVote) -> PollVote:
        """Save a poll vote."""
        pass

    @abstractmethod
    def get_poll_votes(self, poll_id: str) -> List[PollVote]:
        """Get votes for a poll."""
        pass

    @abstractmethod
    def has_user_voted(self, poll_id: str, user_id: str) -> bool:
        """Check if a user has already voted on a poll."""
        pass

    # Chapter marker operations
    @abstractmethod
    def save_chapter_marker(self, marker: ChapterMarker) -> ChapterMarker:
        """Save or update a chapter marker."""
        pass

    @abstractmethod
    def get_chapter_markers(self, video_id: str) -> List[ChapterMarker]:
        """Get chapter markers for a video."""
        pass

    @abstractmethod
    def delete_chapter_marker(self, marker_id: str) -> bool:
        """Delete a chapter marker."""
        pass

    # Product tag operations
    @abstractmethod
    def save_product_tag(self, tag: ProductTag) -> ProductTag:
        """Save or update a product tag."""
        pass

    @abstractmethod
    def get_product_tags(self, video_id: str) -> List[ProductTag]:
        """Get product tags for a video."""
        pass

    @abstractmethod
    def delete_product_tag(self, tag_id: str) -> bool:
        """Delete a product tag."""
        pass

    @abstractmethod
    def increment_product_tag_clicks(self, tag_id: str) -> Optional[ProductTag]:
        """Increment click count for a product tag."""
        pass

    # Video link operations
    @abstractmethod
    def save_video_link(self, link: VideoLink) -> VideoLink:
        """Save or update a video link."""
        pass

    @abstractmethod
    def get_video_links(self, video_id: str) -> List[VideoLink]:
        """Get links for a video."""
        pass

    @abstractmethod
    def delete_video_link(self, link_id: str) -> bool:
        """Delete a video link."""
        pass

    @abstractmethod
    def increment_video_link_clicks(self, link_id: str) -> Optional[VideoLink]:
        """Increment click count for a video link."""
        pass

    # Challenge operations
    @abstractmethod
    def save_challenge(self, challenge: Challenge) -> Challenge:
        """Save or update a challenge."""
        pass

    @abstractmethod
    def get_challenge_by_id(self, challenge_id: str) -> Optional[Challenge]:
        """Get challenge by ID."""
        pass

    @abstractmethod
    def get_active_challenges(self, offset: int = 0, limit: int = 20) -> List[Challenge]:
        """Get active challenges."""
        pass

    @abstractmethod
    def delete_challenge(self, challenge_id: str) -> bool:
        """Delete a challenge."""
        pass

    @abstractmethod
    def save_challenge_participant(self, participant: ChallengeParticipant) -> ChallengeParticipant:
        """Save a challenge participant."""
        pass

    @abstractmethod
    def get_challenge_participants(self, challenge_id: str, offset: int = 0, limit: int = 50) -> List[ChallengeParticipant]:
        """Get participants of a challenge."""
        pass

    # Badge operations
    @abstractmethod
    def save_badge(self, badge: Badge) -> Badge:
        """Save or update a badge."""
        pass

    @abstractmethod
    def get_badge_by_id(self, badge_id: str) -> Optional[Badge]:
        """Get badge by ID."""
        pass

    @abstractmethod
    def get_all_badges(self) -> List[Badge]:
        """Get all available badges."""
        pass

    @abstractmethod
    def save_user_badge(self, user_badge: UserBadge) -> UserBadge:
        """Award a badge to a user."""
        pass

    @abstractmethod
    def get_user_badges(self, user_id: str) -> List[UserBadge]:
        """Get all badges earned by a user."""
        pass

    @abstractmethod
    def has_user_badge(self, user_id: str, badge_id: str) -> bool:
        """Check if a user has a specific badge."""
        pass


class DiscoveryRepositoryPort(ABC):
    """Repository port for discovery features: playlists, preferences, favorite creators, traffic, retention."""

    # Playlist operations
    @abstractmethod
    def save_playlist(self, playlist: Playlist) -> Playlist:
        """Save or update a playlist."""
        pass

    @abstractmethod
    def get_playlist_by_id(self, playlist_id: str) -> Optional[Playlist]:
        """Get playlist by ID."""
        pass

    @abstractmethod
    def get_playlists_by_creator(self, creator_id: str) -> List[Playlist]:
        """Get playlists created by a user."""
        pass

    @abstractmethod
    def get_public_playlists(self, offset: int = 0, limit: int = 20) -> List[Playlist]:
        """Get public playlists."""
        pass

    @abstractmethod
    def delete_playlist(self, playlist_id: str) -> bool:
        """Delete a playlist."""
        pass

    @abstractmethod
    def save_playlist_item(self, item: PlaylistItem) -> PlaylistItem:
        """Save or update a playlist item."""
        pass

    @abstractmethod
    def get_playlist_items(self, playlist_id: str) -> List[PlaylistItem]:
        """Get items in a playlist."""
        pass

    @abstractmethod
    def remove_playlist_item(self, item_id: str) -> bool:
        """Remove an item from a playlist."""
        pass

    @abstractmethod
    def save_playlist_collaborator(self, collaborator: PlaylistCollaborator) -> PlaylistCollaborator:
        """Add a collaborator to a playlist."""
        pass

    @abstractmethod
    def remove_playlist_collaborator(self, playlist_id: str, user_id: str) -> bool:
        """Remove a collaborator from a playlist."""
        pass

    @abstractmethod
    def get_playlist_collaborators(self, playlist_id: str) -> List[PlaylistCollaborator]:
        """Get collaborators for a playlist."""
        pass

    # User preferences operations
    @abstractmethod
    def save_user_preferences(self, preferences: UserPreferences) -> UserPreferences:
        """Save or update user preferences."""
        pass

    @abstractmethod
    def get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Get user preferences."""
        pass

    # Favorite creator operations
    @abstractmethod
    def save_favorite_creator(self, favorite: FavoriteCreator) -> FavoriteCreator:
        """Save a favorite creator."""
        pass

    @abstractmethod
    def remove_favorite_creator(self, user_id: str, creator_id: str) -> bool:
        """Remove a favorite creator."""
        pass

    @abstractmethod
    def get_favorite_creators(self, user_id: str) -> List[FavoriteCreator]:
        """Get favorite creators for a user."""
        pass

    @abstractmethod
    def is_favorite_creator(self, user_id: str, creator_id: str) -> bool:
        """Check if a creator is a user's favorite."""
        pass

    # Traffic source operations
    @abstractmethod
    def save_traffic_source(self, source: TrafficSource) -> TrafficSource:
        """Save a traffic source entry."""
        pass

    @abstractmethod
    def get_traffic_sources_by_video(self, video_id: str) -> List[TrafficSource]:
        """Get traffic sources for a video."""
        pass

    @abstractmethod
    def get_traffic_source_summary(self, video_id: str) -> Dict[str, int]:
        """Get traffic source summary for a video."""
        pass

    # Retention data operations
    @abstractmethod
    def save_retention_data(self, data: RetentionData) -> RetentionData:
        """Save retention data point."""
        pass

    @abstractmethod
    def get_retention_data(self, video_id: str) -> List[RetentionData]:
        """Get retention data for a video."""
        pass

    # Posting time recommendation operations
    @abstractmethod
    def save_posting_time_recommendation(self, recommendation: PostingTimeRecommendation) -> PostingTimeRecommendation:
        """Save or update a posting time recommendation."""
        pass

    @abstractmethod
    def get_posting_time_recommendations(self, user_id: str) -> List[PostingTimeRecommendation]:
        """Get posting time recommendations for a user."""
        pass


class CourseRepositoryPort(ABC):
    """Repository port for course and premium features: courses, lessons, enrollments, subscription tiers."""

    # Course operations
    @abstractmethod
    def save_course(self, course: Course) -> Course:
        """Save or update a course."""
        pass

    @abstractmethod
    def get_course_by_id(self, course_id: str) -> Optional[Course]:
        """Get course by ID."""
        pass

    @abstractmethod
    def get_courses_by_creator(self, creator_id: str) -> List[Course]:
        """Get courses by a creator."""
        pass

    @abstractmethod
    def get_published_courses(self, offset: int = 0, limit: int = 20) -> List[Course]:
        """Get published courses."""
        pass

    @abstractmethod
    def delete_course(self, course_id: str) -> bool:
        """Delete a course."""
        pass

    # Lesson operations
    @abstractmethod
    def save_lesson(self, lesson: CourseLesson) -> CourseLesson:
        """Save or update a course lesson."""
        pass

    @abstractmethod
    def get_lesson_by_id(self, lesson_id: str) -> Optional[CourseLesson]:
        """Get lesson by ID."""
        pass

    @abstractmethod
    def get_course_lessons(self, course_id: str) -> List[CourseLesson]:
        """Get lessons for a course."""
        pass

    @abstractmethod
    def delete_lesson(self, lesson_id: str) -> bool:
        """Delete a lesson."""
        pass

    # Enrollment operations
    @abstractmethod
    def save_enrollment(self, enrollment: CourseEnrollment) -> CourseEnrollment:
        """Save or update a course enrollment."""
        pass

    @abstractmethod
    def get_enrollment_by_id(self, enrollment_id: str) -> Optional[CourseEnrollment]:
        """Get enrollment by ID."""
        pass

    @abstractmethod
    def get_user_enrollments(self, user_id: str) -> List[CourseEnrollment]:
        """Get enrollments for a user."""
        pass

    @abstractmethod
    def get_course_enrollments(self, course_id: str, offset: int = 0, limit: int = 50) -> List[CourseEnrollment]:
        """Get enrollments for a course."""
        pass

    @abstractmethod
    def is_user_enrolled(self, course_id: str, user_id: str) -> bool:
        """Check if a user is enrolled in a course."""
        pass

    # Subscription tier operations
    @abstractmethod
    def save_subscription_tier(self, tier: SubscriptionTier) -> SubscriptionTier:
        """Save or update a subscription tier."""
        pass

    @abstractmethod
    def get_subscription_tier_by_id(self, tier_id: str) -> Optional[SubscriptionTier]:
        """Get subscription tier by ID."""
        pass

    @abstractmethod
    def get_creator_subscription_tiers(self, creator_id: str) -> List[SubscriptionTier]:
        """Get subscription tiers for a creator."""
        pass

    @abstractmethod
    def delete_subscription_tier(self, tier_id: str) -> bool:
        """Delete a subscription tier."""
        pass

    # Creator fund eligibility operations
    @abstractmethod
    def save_creator_fund_eligibility(self, eligibility: CreatorFundEligibility) -> CreatorFundEligibility:
        """Save or update creator fund eligibility."""
        pass

    @abstractmethod
    def get_creator_fund_eligibility(self, user_id: str) -> Optional[CreatorFundEligibility]:
        """Get creator fund eligibility for a user."""
        pass
