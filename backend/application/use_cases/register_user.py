import uuid

from ...domain.entities.user import User
from ...domain.ports.repository_ports import UserRepositoryPort
from ...domain.ports.security_port import PasswordHelperPort
from ..dtos.auth_dto import RegisterRequestDTO, UserResponseDTO


class RegisterUserUseCase:
    def __init__(
        self,
        user_repo: UserRepositoryPort,
        password_helper: PasswordHelperPort,
    ):
        self._user_repo = user_repo
        self._password = password_helper

    def execute(self, dto: RegisterRequestDTO) -> UserResponseDTO:
        existing_user = self._user_repo.get_by_email(dto.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        hashed_pw = self._password.hash(dto.password)

        new_user = User(
            id=str(uuid.uuid4()),
            username=dto.username,
            email=dto.email,
            hashed_password=hashed_pw,
        )

        saved_user = self._user_repo.save(new_user)

        return UserResponseDTO(
            id=saved_user.id,
            username=saved_user.username,
            email=saved_user.email,
            is_active=saved_user.is_active,
        )
