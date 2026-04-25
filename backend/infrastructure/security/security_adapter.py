from passlib.context import CryptContext

from backend.domain.ports.security_port import PasswordHelperPort

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class PasswordHelper(PasswordHelperPort):
    def hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)


SecurityAdapter = PasswordHelper
