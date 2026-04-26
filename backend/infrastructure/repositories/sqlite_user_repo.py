from typing import Optional
from sqlmodel import Session, select
from ...domain.entities.user import User
from ...domain.ports.repository_ports import UserRepositoryPort
from .models import UserDB

# Fields the domain User entity accepts. UserDB has additional columns
# (created_at, updated_at, email_verified) that aren't on the entity.
_USER_FIELDS = {"id", "username", "email", "hashed_password", "is_active", "bio", "avatar_url"}


def _db_to_domain(row: UserDB) -> User:
    raw = row.model_dump()
    return User(**{k: v for k, v in raw.items() if k in _USER_FIELDS})


class SQLiteUserRepository(UserRepositoryPort):
    def __init__(self, session: Session):
        self.session = session

    def save(self, user: User) -> User:
        # Don't blow away DB-only columns when persisting an entity update.
        existing = self.session.get(UserDB, user.id) if user.id else None
        if existing is not None:
            for field in _USER_FIELDS:
                if hasattr(existing, field):
                    setattr(existing, field, getattr(user, field))
            db_user = self.session.merge(existing)
        else:
            db_user = UserDB.model_validate(user)
            db_user = self.session.merge(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return _db_to_domain(db_user)

    def get_by_email(self, email: str) -> Optional[User]:
        statement = select(UserDB).where(UserDB.email == email)
        result = self.session.exec(statement).first()
        return _db_to_domain(result) if result else None

    def get_by_id(self, user_id: str) -> Optional[User]:
        result = self.session.get(UserDB, user_id)
        return _db_to_domain(result) if result else None

    def get_by_username(self, username: str) -> Optional[User]:
        statement = select(UserDB).where(UserDB.username == username)
        result = self.session.exec(statement).first()
        return _db_to_domain(result) if result else None
