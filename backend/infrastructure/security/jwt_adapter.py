from datetime import datetime, timedelta, UTC
from typing import Optional
from jose import jwt, exceptions as jose_exceptions

_settings = None


def _get_settings():
    global _settings
    if _settings is None:
        from infrastructure.config import get_settings

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


class JWTAdapter:
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
        encoded_jwt = jwt.encode(
            to_encode, get_jwt_secret(), algorithm=settings.jwt_algorithm
        )
        return encoded_jwt

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
