from datetime import datetime, UTC
from typing import Iterable

from sqlmodel import Session, select

from backend.domain.ports.push_port import (
    DeviceToken,
    DeviceTokenRepositoryPort,
)

from .models import DeviceTokenDB


class SQLiteDeviceTokenRepository(DeviceTokenRepositoryPort):
    def __init__(self, session: Session):
        self._session = session

    def upsert(self, token: DeviceToken) -> None:
        existing = self._session.get(DeviceTokenDB, token.token)
        now = datetime.now(UTC)
        if existing:
            existing.user_id = token.user_id
            existing.platform = token.platform
            existing.last_seen_at = now
            self._session.add(existing)
        else:
            self._session.add(
                DeviceTokenDB(
                    token=token.token,
                    user_id=token.user_id,
                    platform=token.platform,
                    last_seen_at=now,
                )
            )
        self._session.commit()

    def remove(self, token: str) -> None:
        existing = self._session.get(DeviceTokenDB, token)
        if existing:
            self._session.delete(existing)
            self._session.commit()

    def _to_domain(self, row: DeviceTokenDB) -> DeviceToken:
        return DeviceToken(token=row.token, user_id=row.user_id, platform=row.platform)

    def list_for_user(self, user_id: str) -> list[DeviceToken]:
        rows = self._session.exec(
            select(DeviceTokenDB).where(DeviceTokenDB.user_id == user_id)
        ).all()
        return [self._to_domain(r) for r in rows]

    def list_for_users(self, user_ids: Iterable[str]) -> list[DeviceToken]:
        ids = list(user_ids)
        if not ids:
            return []
        rows = self._session.exec(
            select(DeviceTokenDB).where(DeviceTokenDB.user_id.in_(ids))
        ).all()
        return [self._to_domain(r) for r in rows]
