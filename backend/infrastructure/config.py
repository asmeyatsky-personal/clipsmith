import os
import secrets
from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    environment: str = Field(default="development")

    database_url: str = Field(default="sqlite:///database.db")

    jwt_secret_key: str = Field(default="")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expire_minutes: int = Field(default=30)

    redis_url: Optional[str] = None
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)

    stripe_secret_key: Optional[str] = None
    stripe_publishable_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None

    storage_type: str = Field(default="local")
    upload_dir: str = Field(default="./uploads")
    thumbnail_dir: str = Field(default="./thumbnails")
    storage_base_url: str = Field(default="http://localhost:8000/uploads")

    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = Field(default="us-east-1")
    s3_bucket_name: Optional[str] = None

    gcs_bucket_name: Optional[str] = None
    gcs_project_id: Optional[str] = None
    gcs_cdn_domain: Optional[str] = None

    assemblyai_api_key: Optional[str] = None

    allowed_origins: str = Field(default="http://localhost:3000")
    frontend_url: str = Field(default="http://localhost:3000")
    backend_url: str = Field(default="http://localhost:8000")

    smtp_host: Optional[str] = None
    smtp_port: int = Field(default=587)
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: str = Field(default="noreply@clipsmith.com")
    smtp_use_tls: bool = Field(default=True)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        case_sensitive = False

    @field_validator("jwt_secret_key", mode="before")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if not v or v == "CHANGE_ME_GENERATE_A_REAL_SECRET":
            if os.getenv("ENVIRONMENT") == "production":
                raise ValueError(
                    "JWT_SECRET_KEY must be set to a secure value in production. "
                    'Generate one with: python -c "import secrets; print(secrets.token_urlsafe(64))"'
                )
            return secrets.token_urlsafe(64)
        return v

    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if os.getenv("ENVIRONMENT") == "production" and v.startswith("sqlite"):
            raise ValueError("SQLite is not supported for production. Use PostgreSQL.")
        return v

    def get_redis_url(self) -> str:
        if self.redis_url:
            return self.redis_url
        return f"redis://{self.redis_host}:{self.redis_port}"

    def is_production(self) -> bool:
        return self.environment == "production"

    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
