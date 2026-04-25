"""Ports for password reset and 2FA persistence."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional


class PasswordResetRepositoryPort(ABC):
    @abstractmethod
    def create(self, user_id: str, token: str, expires_at: datetime) -> None: ...

    @abstractmethod
    def find_active_by_token(self, token: str) -> Optional["PasswordResetRecord"]: ...

    @abstractmethod
    def mark_used(self, token: str) -> None: ...

    @abstractmethod
    def update_user_password(self, user_id: str, new_hash: str) -> None: ...


class TwoFactorRepositoryPort(ABC):
    @abstractmethod
    def get_active(self, user_id: str) -> Optional["TwoFactorRecord"]: ...

    @abstractmethod
    def get_pending(self, user_id: str) -> Optional["TwoFactorRecord"]: ...

    @abstractmethod
    def create_pending(
        self, user_id: str, method: str, secret: str, backup_codes: list[str]
    ) -> None: ...

    @abstractmethod
    def activate_pending(self, user_id: str) -> bool: ...

    @abstractmethod
    def delete_all_for_user(self, user_id: str) -> None: ...


class PasswordResetRecord:
    def __init__(self, user_id: str, token: str, expires_at: datetime, used: bool):
        self.user_id = user_id
        self.token = token
        self.expires_at = expires_at
        self.used = used


class TwoFactorRecord:
    def __init__(
        self,
        user_id: str,
        method: str,
        secret: str,
        backup_codes: list[str],
        is_active: bool,
    ):
        self.user_id = user_id
        self.method = method
        self.secret = secret
        self.backup_codes = backup_codes
        self.is_active = is_active
