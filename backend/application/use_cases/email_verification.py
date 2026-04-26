"""Email verification use cases (A2).

On register, a token is generated, persisted, and emailed. The user clicks
the link → POST /auth/verify-email/{token} flips email_verified=true.
"""
from __future__ import annotations

import os
import secrets
from datetime import UTC, datetime, timedelta

from ...domain.ports.email_port import EmailSenderPort
from ...domain.ports.email_verification_port import (
    EmailVerificationRecord,
    EmailVerificationRepositoryPort,
)
from ...domain.ports.repository_ports import UserRepositoryPort

VERIFICATION_TOKEN_TTL = timedelta(hours=24)


class RequestEmailVerificationUseCase:
    def __init__(
        self,
        user_repo: UserRepositoryPort,
        verification_repo: EmailVerificationRepositoryPort,
        email_sender: EmailSenderPort,
        frontend_url: str | None = None,
    ):
        self._users = user_repo
        self._verifications = verification_repo
        self._email = email_sender
        self._frontend_url = frontend_url or os.getenv(
            "FRONTEND_URL", "http://localhost:3000"
        )

    def execute(self, user_id: str) -> str:
        user = self._users.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        token = secrets.token_urlsafe(32)
        record = EmailVerificationRecord(
            user_id=user.id,
            email=user.email,
            token=token,
            expires_at=datetime.now(UTC) + VERIFICATION_TOKEN_TTL,
        )
        self._verifications.create(record)

        verify_url = f"{self._frontend_url}/verify-email?token={token}"
        body = (
            f"Hi {user.username},\n\n"
            "Welcome to Clipsmith. Please confirm your email by clicking:\n\n"
            f"{verify_url}\n\n"
            "This link expires in 24 hours.\n\n"
            "If you didn't create an account, ignore this email."
        )
        self._email.send(
            to=user.email,
            subject="Verify your Clipsmith email",
            body=body,
            html_body=None,
        )
        return token


class ConfirmEmailVerificationUseCase:
    def __init__(self, verification_repo: EmailVerificationRepositoryPort):
        self._verifications = verification_repo

    def execute(self, token: str) -> bool:
        record = self._verifications.find_active_by_token(token)
        if not record:
            return False
        self._verifications.mark_verified(token)
        self._verifications.mark_user_email_verified(record.user_id)
        return True
