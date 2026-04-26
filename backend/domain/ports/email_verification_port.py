"""Port for email verification token persistence."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class EmailVerificationRecord:
    user_id: str
    email: str
    token: str
    expires_at: datetime
    status: str = "pending"


class EmailVerificationRepositoryPort(ABC):
    @abstractmethod
    def create(self, record: EmailVerificationRecord) -> None: ...

    @abstractmethod
    def find_active_by_token(
        self, token: str
    ) -> Optional[EmailVerificationRecord]: ...

    @abstractmethod
    def mark_verified(self, token: str) -> None: ...

    @abstractmethod
    def mark_user_email_verified(self, user_id: str) -> None: ...
