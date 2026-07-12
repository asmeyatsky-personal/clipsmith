import secrets
from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field, model_validator


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
    storage_backend: Optional[str] = None
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

    # Auth cookie attributes. The iOS (Capacitor) app is served from
    # capacitor://localhost and calls the API on another origin, so the cookie
    # must be SameSite=None; Secure to be sent cross-site. Web-only deployments
    # can keep the stricter "lax". Secure must be False for local http dev or
    # the cookie is dropped.
    cookie_samesite: str = Field(default="lax")  # lax | strict | none
    cookie_secure: bool = Field(default=True)

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

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Enforce production-safe settings against the *parsed* environment
        field. Gating on ``self.environment`` (not ``os.getenv``) is what makes
        this correct: pydantic-settings loads ENVIRONMENT from .env without
        exporting it to ``os.environ``, so an os.getenv check would silently
        skip these guards when ENVIRONMENT is only set in the .env file.
        """
        is_prod = self.environment == "production"

        if not self.jwt_secret_key or self.jwt_secret_key == "CHANGE_ME_GENERATE_A_REAL_SECRET":
            if is_prod:
                raise ValueError(
                    "JWT_SECRET_KEY must be set to a secure value in production. "
                    'Generate one with: python -c "import secrets; print(secrets.token_urlsafe(64))"'
                )
            # Dev/test convenience: generate an ephemeral secret.
            self.jwt_secret_key = secrets.token_urlsafe(64)

        if is_prod and self.database_url.startswith("sqlite"):
            raise ValueError("SQLite is not supported for production. Use PostgreSQL.")

        # Local filesystem storage is ephemeral and per-machine; on a multi-machine
        # deploy (API + worker) uploads written by one machine are invisible to the
        # other and lost on redeploy. Require object storage in production.
        effective_storage = (self.storage_backend or self.storage_type or "local").lower()
        if is_prod and effective_storage == "local":
            raise ValueError(
                "Local filesystem storage is not supported in production. "
                "Set STORAGE_TYPE to one of: s3, r2, gcs."
            )

        return self

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
