from sqlmodel import Session, select

from backend.domain.ports.user_block_port import UserBlockRepositoryPort

from .models import UserBlockDB


class SQLiteUserBlockRepository(UserBlockRepositoryPort):
    def __init__(self, session: Session):
        self._session = session

    def block(self, blocker_id: str, blocked_id: str) -> None:
        existing = self._session.get(UserBlockDB, (blocker_id, blocked_id))
        if existing:
            return
        self._session.add(UserBlockDB(blocker_id=blocker_id, blocked_id=blocked_id))
        self._session.commit()

    def unblock(self, blocker_id: str, blocked_id: str) -> None:
        existing = self._session.get(UserBlockDB, (blocker_id, blocked_id))
        if existing:
            self._session.delete(existing)
            self._session.commit()

    def is_blocked(self, blocker_id: str, blocked_id: str) -> bool:
        return self._session.get(UserBlockDB, (blocker_id, blocked_id)) is not None

    def list_blocked_ids(self, blocker_id: str) -> list[str]:
        rows = self._session.exec(
            select(UserBlockDB).where(UserBlockDB.blocker_id == blocker_id)
        ).all()
        return [r.blocked_id for r in rows]

    def list_blockers_of(self, blocked_id: str) -> list[str]:
        rows = self._session.exec(
            select(UserBlockDB).where(UserBlockDB.blocked_id == blocked_id)
        ).all()
        return [r.blocker_id for r in rows]
