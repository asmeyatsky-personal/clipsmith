from typing import Optional

from ...domain.ports.repository_ports import UserRepositoryPort
from ...domain.ports.security_port import JWTPort, PasswordHelperPort
from ..dtos.auth_dto import LoginRequestDTO, LoginResponseDTO, UserResponseDTO


class AuthenticateUserUseCase:
    def __init__(
        self,
        user_repo: UserRepositoryPort,
        password_helper: PasswordHelperPort,
        jwt: JWTPort,
        access_token_seconds: int = 1800,
    ):
        self._user_repo = user_repo
        self._password = password_helper
        self._jwt = jwt
        self._access_token_seconds = access_token_seconds

    def execute(self, dto: LoginRequestDTO) -> Optional[LoginResponseDTO]:
        user = self._user_repo.get_by_email(dto.email)
        if not user:
            return None

        if not self._password.verify(dto.password, user.hashed_password):
            return None

        access_token = self._jwt.encode(
            claims={"sub": user.email, "user_id": user.id},
            expires_in_seconds=self._access_token_seconds,
        )

        return LoginResponseDTO(
            access_token=access_token,
            user=UserResponseDTO(
                id=user.id,
                username=user.username,
                email=user.email,
                is_active=user.is_active,
            ),
        )
