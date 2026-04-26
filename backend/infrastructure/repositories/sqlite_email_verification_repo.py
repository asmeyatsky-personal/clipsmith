from datetime import UTC, datetime
from typing import Optional

from sqlmodel import Session, select

from backend.domain.ports.email_verification_port import (
    EmailVerificationRecord,
    EmailVerificationRepositoryPort,
)

from .models import EmailVerificationDB, UserDB


class SQLiteEmailVerificationRepository(EmailVerificationRepositoryPort):
    def __init__(self, session: Session):
        self._session = session

    def create(self, record: EmailVerificationRecord) -> None:
        row = EmailVerificationDB(
            user_id=record.user_id,
            email=record.email,
            token=record.token,
            status=record.status,
            expires_at=record.expires_at,
        )
        self._session.add(row)
        self._session.commit()

    def find_active_by_token(self, token: str) -> Optional[EmailVerificationRecord]:
        stmt = select(EmailVerificationDB).where(
            EmailVerificationDB.token == token,
            EmailVerificationDB.status == "pending",
            EmailVerificationDB.expires_at > datetime.now(UTC),
        )
        row = self._session.exec(stmt).first()
        if not row:
            return None
        return EmailVerificationRecord(
            user_id=row.user_id,
            email=row.email,
            token=row.token,
            expires_at=row.expires_at,
            status=row.status,
        )

    def mark_verified(self, token: str) -> None:
        stmt = select(EmailVerificationDB).where(EmailVerificationDB.token == token)
        row = self._session.exec(stmt).first()
        if row:
            row.status = "verified"
            row.verified_at = datetime.now(UTC)
            self._session.add(row)
            self._session.commit()

    def mark_user_email_verified(self, user_id: str) -> None:
        user = self._session.get(UserDB, user_id)
        if user:
            user.email_verified = True
            self._session.add(user)
            self._session.commit()
