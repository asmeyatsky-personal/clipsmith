import logging
from typing import List, Optional, Dict, Any
from datetime import UTC, date, datetime

logger = logging.getLogger(__name__)


class ComplianceService:
    """Service for GDPR, CCPA, and COPPA compliance operations."""

    def __init__(self, repository):
        self.repository = repository

    # GDPR request operations
    async def submit_gdpr_request(
        self, user_id: str, request_type: str
    ) -> Dict[str, Any]:
        """Submit a GDPR request (data_export, deletion, access, rectification, portability)."""
        from ...infrastructure.repositories.models import GDPRRequestDB

        valid_types = [
            "data_export",
            "deletion",
            "consent_withdrawal",
            "access",
            "rectification",
            "portability",
        ]
        if request_type not in valid_types:
            return {
                "success": False,
                "error": f"Invalid request type. Must be one of: {', '.join(valid_types)}",
            }

        request = GDPRRequestDB(
            user_id=user_id,
            request_type=request_type,
            status="pending",
        )
        saved = self.repository.save_gdpr_request(request)
        return {"success": True, "request_id": saved.id}

    async def process_gdpr_request(self, request_id: str) -> Dict[str, Any]:
        """Process a pending GDPR request based on its type."""
        request = self.repository.get_gdpr_request(request_id)
        if not request:
            return {"success": False, "error": "Request not found"}
        if request.status != "pending":
            return {"success": False, "error": f"Request is already {request.status}"}

        self.repository.update_gdpr_request_status(request_id, "processing")

        try:
            if request.request_type == "data_export":
                result = await self.export_user_data(request.user_id)
                result_url = result.get("export_url")
                self.repository.update_gdpr_request_result(
                    request_id, result_url=result_url
                )
            elif request.request_type == "deletion":
                await self.delete_user_data(request.user_id)
            elif request.request_type == "access":
                result = await self.export_user_data(request.user_id)
                result_url = result.get("export_url")
                self.repository.update_gdpr_request_result(
                    request_id, result_url=result_url
                )
            elif request.request_type == "portability":
                result = await self.export_user_data(request.user_id)
                result_url = result.get("export_url")
                self.repository.update_gdpr_request_result(
                    request_id, result_url=result_url
                )
            elif request.request_type == "consent_withdrawal":
                await self.withdraw_consent(request.user_id, consent_type="all")

            self.repository.update_gdpr_request_status(
                request_id, "completed", completed_at=datetime.now(UTC)
            )
            return {"success": True, "status": "completed"}

        except Exception as e:
            logger.error(f"Error processing GDPR request {request_id}: {e}")
            self.repository.update_gdpr_request_status(request_id, "failed")
            return {"success": False, "error": str(e)}

    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Collect all user data from all tables and return as JSON."""
        import json

        user_data = {}

        # Collect data from all relevant tables
        user_data["profile"] = self.repository.get_user_profile_data(user_id)
        user_data["videos"] = self.repository.get_user_videos_data(user_id)
        user_data["comments"] = self.repository.get_user_comments_data(user_id)
        user_data["likes"] = self.repository.get_user_likes_data(user_id)
        user_data["follows"] = self.repository.get_user_follows_data(user_id)
        user_data["tips"] = self.repository.get_user_tips_data(user_id)
        user_data["transactions"] = self.repository.get_user_transactions_data(user_id)
        user_data["messages"] = self.repository.get_user_messages_data(user_id)
        user_data["notifications"] = self.repository.get_user_notifications_data(
            user_id
        )
        user_data["preferences"] = self.repository.get_user_preferences_data(user_id)
        user_data["consents"] = self.repository.get_user_consents_data(user_id)

        # Store the export and generate a URL
        export_json = json.dumps(user_data, default=str)
        export_url = self.repository.store_data_export(user_id, export_json)

        return {
            "success": True,
            "user_data": user_data,
            "export_url": export_url,
        }

    async def delete_user_data(
        self, user_id: str, categories: List[str] = None
    ) -> Dict[str, Any]:
        """Delete specified categories of user data, or all data if no categories specified."""
        all_categories = [
            "videos",
            "comments",
            "likes",
            "follows",
            "tips",
            "messages",
            "notifications",
            "preferences",
            "analytics",
        ]

        categories_to_delete = categories if categories else all_categories
        deleted = []

        for category in categories_to_delete:
            try:
                self.repository.delete_user_data_category(user_id, category)
                deleted.append(category)
            except Exception as e:
                logger.error(
                    f"Error deleting {category} data for user {user_id}: {e}"
                )

        return {"success": True, "deleted_categories": deleted}

    # Consent management
    async def record_consent(
        self,
        user_id: str,
        consent_type: str,
        granted: bool,
        ip_address: str = None,
    ) -> Dict[str, Any]:
        """Record a user's consent decision."""
        from ...infrastructure.repositories.models import ConsentRecordDB

        consent = ConsentRecordDB(
            user_id=user_id,
            consent_type=consent_type,
            granted=granted,
            ip_address=ip_address,
        )
        saved = self.repository.save_consent_record(consent)
        return {"success": True, "consent": saved}

    async def get_user_consents(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all consent records for a user."""
        return self.repository.get_consent_records(user_id)

    async def withdraw_consent(
        self, user_id: str, consent_type: str
    ) -> Dict[str, Any]:
        """Withdraw a previously granted consent."""
        if consent_type == "all":
            consents = self.repository.get_consent_records(user_id)
            for consent in consents:
                if consent.granted:
                    self.repository.update_consent_record(
                        consent.id, granted=False
                    )
            return {"success": True, "withdrawn": "all"}

        consent = self.repository.get_consent_by_type(user_id, consent_type)
        if not consent:
            return {"success": False, "error": "Consent record not found"}

        self.repository.update_consent_record(consent.id, granted=False)
        return {"success": True, "consent_type": consent_type}

    # COPPA compliance
    async def verify_age(
        self, user_id: str, date_of_birth: date
    ) -> Dict[str, Any]:
        """Verify a user's age for COPPA compliance (under 13 requires parental consent)."""
        today = date.today()
        age = (
            today.year
            - date_of_birth.year
            - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        )

        requires_parental_consent = age < 13
        is_minor = age < 18

        self.repository.save_age_verification(
            user_id=user_id,
            date_of_birth=date_of_birth,
            age=age,
            requires_parental_consent=requires_parental_consent,
        )

        return {
            "success": True,
            "age": age,
            "is_minor": is_minor,
            "requires_parental_consent": requires_parental_consent,
            "coppa_restricted": requires_parental_consent,
        }

    # CCPA compliance
    async def get_ccpa_data(self, user_id: str) -> Dict[str, Any]:
        """Return all data for a CCPA 'right to know' request."""
        result = await self.export_user_data(user_id)
        return {
            "success": True,
            "ccpa_data": result.get("user_data", {}),
            "categories_collected": list(result.get("user_data", {}).keys()),
        }

    async def opt_out_data_sale(self, user_id: str) -> Dict[str, Any]:
        """Implement CCPA 'do not sell my personal information'."""
        # Record the opt-out as a consent record
        await self.record_consent(
            user_id=user_id,
            consent_type="data_sale",
            granted=False,
        )

        # Update user preferences to disable data sharing
        self.repository.set_data_sale_opt_out(user_id, opted_out=True)

        return {"success": True, "opted_out": True}
