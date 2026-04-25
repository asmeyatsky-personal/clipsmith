"""SQLModel adapters implementing auth-security ports."""
from datetime import datetime
from typing import Optional

from sqlmodel import Session, select

from backend.domain.ports.auth_security_port import (
    PasswordResetRecord,
    PasswordResetRepositoryPort,
    TwoFactorRecord,
    TwoFactorRepositoryPort,
)

from .models import PasswordResetDB, TwoFactorSecretDB, UserDB


class SQLitePasswordResetRepository(PasswordResetRepositoryPort):
    def __init__(self, session: Session):
        self._session = session

    def create(self, user_id: str, token: str, expires_at: datetime) -> None:
        rec = PasswordResetDB(user_id=user_id, token=token, expires_at=expires_at)
        self._session.add(rec)
        self._session.commit()

    def find_active_by_token(self, token: str) -> Optional[PasswordResetRecord]:
        stmt = select(PasswordResetDB).where(
            PasswordResetDB.token == token,
            PasswordResetDB.used == False,  # noqa: E712
            PasswordResetDB.expires_at > datetime.now(),
        )
        row = self._session.exec(stmt).first()
        if not row:
            return None
        return PasswordResetRecord(
            user_id=row.user_id,
            token=row.token,
            expires_at=row.expires_at,
            used=row.used,
        )

    def mark_used(self, token: str) -> None:
        stmt = select(PasswordResetDB).where(PasswordResetDB.token == token)
        row = self._session.exec(stmt).first()
        if row:
            row.used = True
            self._session.add(row)
            self._session.commit()

    def update_user_password(self, user_id: str, new_hash: str) -> None:
        user_db = self._session.get(UserDB, user_id)
        if user_db:
            user_db.hashed_password = new_hash
            user_db.updated_at = datetime.now()
            self._session.add(user_db)
            self._session.commit()


class SQLiteTwoFactorRepository(TwoFactorRepositoryPort):
    def __init__(self, session: Session):
        self._session = session

    def _to_record(self, row: TwoFactorSecretDB) -> TwoFactorRecord:
        codes = row.backup_codes.split(",") if row.backup_codes else []
        return TwoFactorRecord(
            user_id=row.user_id,
            method=row.method,
            secret=row.secret,
            backup_codes=codes,
            is_active=row.is_active,
        )

    def get_active(self, user_id: str) -> Optional[TwoFactorRecord]:
        stmt = select(TwoFactorSecretDB).where(
            TwoFactorSecretDB.user_id == user_id,
            TwoFactorSecretDB.is_active == True,  # noqa: E712
        )
        row = self._session.exec(stmt).first()
        return self._to_record(row) if row else None

    def get_pending(self, user_id: str) -> Optional[TwoFactorRecord]:
        stmt = select(TwoFactorSecretDB).where(
            TwoFactorSecretDB.user_id == user_id,
            TwoFactorSecretDB.is_active == False,  # noqa: E712
        )
        row = self._session.exec(stmt).first()
        return self._to_record(row) if row else None

    def create_pending(
        self, user_id: str, method: str, secret: str, backup_codes: list[str]
    ) -> None:
        rec = TwoFactorSecretDB(
            user_id=user_id,
            method=method,
            secret=secret,
            backup_codes=",".join(backup_codes),
            is_active=False,
        )
        self._session.add(rec)
        self._session.commit()

    def activate_pending(self, user_id: str) -> bool:
        stmt = select(TwoFactorSecretDB).where(
            TwoFactorSecretDB.user_id == user_id,
            TwoFactorSecretDB.is_active == False,  # noqa: E712
        )
        row = self._session.exec(stmt).first()
        if not row:
            return False
        row.is_active = True
        self._session.add(row)
        self._session.commit()
        return True

    def delete_all_for_user(self, user_id: str) -> None:
        self._session.query(TwoFactorSecretDB).filter(
            TwoFactorSecretDB.user_id == user_id
        ).delete()
        self._session.commit()
