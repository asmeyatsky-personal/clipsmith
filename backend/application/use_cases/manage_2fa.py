"""2FA enrollment, verification, and disable use cases."""
from typing import NamedTuple

from ...domain.ports.auth_security_port import TwoFactorRepositoryPort
from ...domain.ports.repository_ports import UserRepositoryPort
from ...domain.ports.security_port import PasswordHelperPort


class TwoFactorStatus(NamedTuple):
    enabled: bool
    method: str | None


class TwoFactorSetupResult(NamedTuple):
    secret: str
    qr_code_b64: str
    backup_codes: list[str]


class GetTwoFactorStatusUseCase:
    def __init__(self, repo: TwoFactorRepositoryPort):
        self._repo = repo

    def execute(self, user_id: str) -> TwoFactorStatus:
        active = self._repo.get_active(user_id)
        if not active:
            return TwoFactorStatus(enabled=False, method=None)
        return TwoFactorStatus(enabled=True, method=active.method)


class SetupTwoFactorUseCase:
    def __init__(self, repo: TwoFactorRepositoryPort, two_factor_service):
        self._repo = repo
        self._service = two_factor_service

    def execute(self, user_id: str, email: str, method: str) -> TwoFactorSetupResult:
        if self._repo.get_active(user_id):
            raise ValueError("2FA is already enabled. Disable it first.")
        secret, qr_code, backup_codes = self._service.setup_2fa(
            user_id=user_id, method=method, email=email
        )
        self._repo.create_pending(
            user_id=user_id, method=method, secret=secret, backup_codes=backup_codes
        )
        return TwoFactorSetupResult(
            secret=secret, qr_code_b64=qr_code, backup_codes=backup_codes
        )


class VerifyTwoFactorSetupUseCase:
    def __init__(self, repo: TwoFactorRepositoryPort, two_factor_service):
        self._repo = repo
        self._service = two_factor_service

    def execute(self, user_id: str, code: str) -> bool:
        pending = self._repo.get_pending(user_id)
        if not pending:
            raise ValueError("No pending 2FA setup. Start setup first.")
        if not self._service.verify_totp_code(pending.secret, code):
            return False
        return self._repo.activate_pending(user_id)


class DisableTwoFactorUseCase:
    def __init__(
        self,
        repo: TwoFactorRepositoryPort,
        user_repo: UserRepositoryPort,
        password_helper: PasswordHelperPort,
    ):
        self._repo = repo
        self._users = user_repo
        self._password = password_helper

    def execute(self, user_id: str, password: str) -> None:
        user = self._users.get_by_id(user_id)
        if not user or not self._password.verify(password, user.hashed_password):
            raise ValueError("Invalid password")
        self._repo.delete_all_for_user(user_id)


class VerifyLoginTwoFactorUseCase:
    def __init__(self, repo: TwoFactorRepositoryPort, two_factor_service):
        self._repo = repo
        self._service = two_factor_service

    def execute(self, user_id: str, code: str) -> bool:
        active = self._repo.get_active(user_id)
        if not active:
            return False
        return self._service.verify_totp_code(active.secret, code)
