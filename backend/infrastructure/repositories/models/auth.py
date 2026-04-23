from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime, UTC
import uuid


class EmailVerificationDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    email: str = Field(index=True)
    token: str = Field(unique=True, index=True)
    status: str = Field(default="pending", index=True)
    expires_at: datetime = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    verified_at: Optional[datetime] = None


class TwoFactorSecretDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    method: str = Field(index=True)
    secret: str = Field(unique=True)
    backup_codes: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_used_at: Optional[datetime] = None


class TwoFactorVerificationDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    secret_id: str = Field(index=True)
    code: str = Field(index=True)
    expires_at: datetime = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    used_at: Optional[datetime] = None
    is_verified: bool = Field(default=False)
