from datetime import datetime, timedelta, UTC
from typing import Optional
from jose import jwt, exceptions as jose_exceptions

from backend.domain.ports.security_port import JWTPort

_settings = None


def _get_settings():
    global _settings
    if _settings is None:
        from backend.infrastructure.config import get_settings

        _settings = get_settings()
    return _settings


def get_jwt_secret() -> str:
    secret = _get_settings().jwt_secret_key
    if not secret:
        raise RuntimeError(
            "JWT_SECRET_KEY environment variable is required. "
            'Generate one with: python -c "import secrets; print(secrets.token_urlsafe(64))"'
        )
    return secret


class JWTAdapter(JWTPort):
    def encode(self, claims: dict, expires_in_seconds: int) -> str:
        settings = _get_settings()
        to_encode = claims.copy()
        to_encode["exp"] = datetime.now(UTC) + timedelta(seconds=expires_in_seconds)
        return jwt.encode(to_encode, get_jwt_secret(), algorithm=settings.jwt_algorithm)

    def decode(self, token: str) -> dict:
        settings = _get_settings()
        try:
            return jwt.decode(token, get_jwt_secret(), algorithms=[settings.jwt_algorithm])
        except jose_exceptions.JWTError as exc:
            raise ValueError("Invalid token") from exc

    @staticmethod
    def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        settings = _get_settings()
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, get_jwt_secret(), algorithm=settings.jwt_algorithm)

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        try:
            settings = _get_settings()
            payload = jwt.decode(
                token, get_jwt_secret(), algorithms=[settings.jwt_algorithm]
            )
            return payload
        except jose_exceptions.JWTError:
            return None
