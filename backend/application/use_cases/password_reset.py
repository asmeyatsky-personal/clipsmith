"""Password reset use cases."""
import os
import secrets
from datetime import datetime, timedelta

from ...domain.ports.auth_security_port import PasswordResetRepositoryPort
from ...domain.ports.email_port import EmailSenderPort
from ...domain.ports.repository_ports import UserRepositoryPort
from ...domain.ports.security_port import PasswordHelperPort


class RequestPasswordResetUseCase:
    def __init__(
        self,
        user_repo: UserRepositoryPort,
        reset_repo: PasswordResetRepositoryPort,
        email_sender: EmailSenderPort,
        token_ttl_hours: int = 1,
        frontend_url: str | None = None,
    ):
        self._users = user_repo
        self._resets = reset_repo
        self._email = email_sender
        self._token_ttl = timedelta(hours=token_ttl_hours)
        self._frontend_url = frontend_url or os.getenv(
            "FRONTEND_URL", "http://localhost:3000"
        )

    def execute(self, email: str) -> None:
        """Always returns silently — caller responds with generic message."""
        user = self._users.get_by_email(email)
        if not user:
            return

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + self._token_ttl
        self._resets.create(user_id=user.id, token=token, expires_at=expires_at)

        reset_url = f"{self._frontend_url}/reset-password?token={token}"
        body = (
            f"Hi {user.username},\n\n"
            "You requested a password reset for your Clipsmith account.\n\n"
            f"Click the link below to reset your password:\n{reset_url}\n\n"
            "This link will expire in 1 hour.\n\n"
            "If you didn't request this, you can safely ignore this email.\n\n"
            "Best,\nThe Clipsmith Team"
        )
        self._email.send(
            to=user.email,
            subject="Reset your Clipsmith password",
            body=body,
            html_body=None,
        )


class ConfirmPasswordResetUseCase:
    def __init__(
        self,
        user_repo: UserRepositoryPort,
        reset_repo: PasswordResetRepositoryPort,
        password_helper: PasswordHelperPort,
    ):
        self._users = user_repo
        self._resets = reset_repo
        self._password = password_helper

    def execute(self, token: str, new_password: str) -> None:
        record = self._resets.find_active_by_token(token)
        if not record:
            raise ValueError("Invalid or expired reset token")

        user = self._users.get_by_id(record.user_id)
        if not user:
            raise ValueError("User not found")

        new_hash = self._password.hash(new_password)
        self._resets.update_user_password(user.id, new_hash)
        self._resets.mark_used(token)
