from typing import List, Optional, Dict, Any
from datetime import UTC, datetime


class CourseService:
    """Service for courses, subscription tiers, and creator fund eligibility."""

    def __init__(self, repository):
        self.repository = repository

    # Course operations
    async def create_course(
        self,
        creator_id: str,
        title: str,
        description: str = "",
        price: float = 0.0,
        category: str = "general",
    ) -> Dict[str, Any]:
        """Create a new course."""
        from ...infrastructure.repositories.models import CourseDB

        course = CourseDB(
            creator_id=creator_id,
            title=title,
            description=description,
            price=price,
            category=category,
            status="draft",
        )
        saved = self.repository.save_course(course)
        return {"success": True, "course": saved}

    async def add_lesson(
        self,
        course_id: str,
        creator_id: str,
        title: str,
        description: str = "",
        video_id: str = None,
        position: int = 0,
        is_free_preview: bool = False,
    ) -> Dict[str, Any]:
        """Add a lesson to a course."""
        from ...infrastructure.repositories.models import CourseLessonDB

        course = self.repository.get_course(course_id)
        if not course:
            return {"success": False, "error": "Course not found"}
        if course.creator_id != creator_id:
            return {"success": False, "error": "Only the course creator can add lessons"}

        lesson = CourseLessonDB(
            course_id=course_id,
            title=title,
            description=description,
            video_id=video_id,
            position=position,
            is_free_preview=is_free_preview,
        )
        saved = self.repository.save_course_lesson(lesson)
        return {"success": True, "lesson": saved}

    async def enroll_in_course(
        self, course_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Enroll a user in a course."""
        from ...infrastructure.repositories.models import CourseEnrollmentDB

        course = self.repository.get_course(course_id)
        if not course:
            return {"success": False, "error": "Course not found"}

        # Check if already enrolled
        existing = self.repository.get_enrollment(course_id, user_id)
        if existing:
            return {"success": False, "error": "Already enrolled in this course"}

        # Check if the course requires purchase (price > 0)
        if course.price > 0:
            has_purchased = self.repository.check_course_purchase(course_id, user_id)
            if not has_purchased:
                return {"success": False, "error": "Course purchase required"}

        enrollment = CourseEnrollmentDB(
            course_id=course_id,
            user_id=user_id,
            status="enrolled",
        )
        saved = self.repository.save_enrollment(enrollment)
        self.repository.increment_course_enrollment_count(course_id)
        return {"success": True, "enrollment": saved}

    async def update_lesson_progress(
        self, course_id: str, user_id: str, lesson_id: str
    ) -> Dict[str, Any]:
        """Update a user's progress in a course after completing a lesson."""
        enrollment = self.repository.get_enrollment(course_id, user_id)
        if not enrollment:
            return {"success": False, "error": "Not enrolled in this course"}

        # Calculate new progress
        total_lessons = self.repository.count_course_lessons(course_id)
        if total_lessons == 0:
            return {"success": False, "error": "Course has no lessons"}

        self.repository.mark_lesson_completed(enrollment.id, lesson_id)
        completed_lessons = self.repository.count_completed_lessons(
            enrollment.id
        )
        progress_percentage = (completed_lessons / total_lessons) * 100

        self.repository.update_enrollment_progress(
            enrollment.id, progress_percentage
        )

        # Mark as completed if all lessons done
        if progress_percentage >= 100.0:
            self.repository.complete_enrollment(enrollment.id, datetime.now(UTC))

        return {
            "success": True,
            "progress_percentage": progress_percentage,
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons,
        }

    async def get_course(self, course_id: str) -> Dict[str, Any]:
        """Get a course with its lessons."""
        course = self.repository.get_course(course_id)
        if not course:
            return {"success": False, "error": "Course not found"}
        lessons = self.repository.get_course_lessons(course_id)
        return {"success": True, "course": course, "lessons": lessons}

    async def get_creator_courses(
        self, creator_id: str
    ) -> List[Dict[str, Any]]:
        """Get all courses created by a creator."""
        return self.repository.get_courses_by_creator(creator_id)

    async def get_enrolled_courses(
        self, user_id: str
    ) -> List[Dict[str, Any]]:
        """Get all courses a user is enrolled in, with progress."""
        return self.repository.get_enrollments_by_user(user_id)

    # Subscription tier operations
    async def create_subscription_tier(
        self,
        creator_id: str,
        name: str,
        price: float,
        interval: str = "month",
        description: str = "",
        benefits: List[str] = None,
    ) -> Dict[str, Any]:
        """Create a subscription tier for a creator."""
        from ...infrastructure.repositories.models import SubscriptionTierDB
        import json

        tier = SubscriptionTierDB(
            creator_id=creator_id,
            name=name,
            price=price,
            interval=interval,
            description=description,
            benefits=json.dumps(benefits or []),
        )
        saved = self.repository.save_subscription_tier(tier)
        return {"success": True, "subscription_tier": saved}

    async def get_subscription_tiers(
        self, creator_id: str
    ) -> List[Dict[str, Any]]:
        """Get all subscription tiers for a creator."""
        return self.repository.get_subscription_tiers_by_creator(creator_id)

    # Creator fund operations
    async def check_creator_fund_eligibility(
        self, user_id: str, follower_count: int, monthly_views: int
    ) -> Dict[str, Any]:
        """Check if a creator meets the Creator Fund eligibility thresholds."""
        from ...infrastructure.repositories.models import CreatorFundEligibilityDB

        # PRD thresholds: 1000 followers + 10000 monthly views
        is_eligible = follower_count >= 1000 and monthly_views >= 10000

        existing = self.repository.get_creator_fund_eligibility(user_id)
        if existing:
            self.repository.update_creator_fund_eligibility(
                user_id,
                follower_count=follower_count,
                monthly_views=monthly_views,
                is_eligible=is_eligible,
            )
        else:
            eligibility = CreatorFundEligibilityDB(
                user_id=user_id,
                follower_count=follower_count,
                monthly_views=monthly_views,
                is_eligible=is_eligible,
                applied_at=datetime.now(UTC) if is_eligible else None,
                status="approved" if is_eligible else "pending",
            )
            self.repository.save_creator_fund_eligibility(eligibility)

        return {
            "success": True,
            "is_eligible": is_eligible,
            "follower_count": follower_count,
            "monthly_views": monthly_views,
            "requirements": {
                "min_followers": 1000,
                "min_monthly_views": 10000,
                "followers_met": follower_count >= 1000,
                "views_met": monthly_views >= 10000,
            },
        }

    async def get_creator_fund_status(self, user_id: str) -> Dict[str, Any]:
        """Get the creator fund eligibility status for a user."""
        eligibility = self.repository.get_creator_fund_eligibility(user_id)
        if not eligibility:
            return {
                "success": True,
                "status": "not_applied",
                "is_eligible": False,
            }
        return {
            "success": True,
            "status": eligibility.status,
            "is_eligible": eligibility.is_eligible,
            "follower_count": eligibility.follower_count,
            "monthly_views": eligibility.monthly_views,
            "applied_at": eligibility.applied_at,
            "approved_at": eligibility.approved_at,
        }
