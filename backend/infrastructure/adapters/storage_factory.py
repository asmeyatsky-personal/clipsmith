import os
import logging
from typing import Union
from .file_storage_adapter import FileSystemStorageAdapter
from .s3_storage_adapter import S3StorageAdapter
from ...domain.ports.storage_port import StoragePort

logger = logging.getLogger(__name__)


def create_storage_adapter() -> StoragePort:
    """Factory function to create appropriate storage adapter based on environment.

    Supports STORAGE_TYPE (existing) and STORAGE_BACKEND (alternative) env vars.
    Valid values: local, s3, gcs
    """

    # Support both STORAGE_TYPE (existing) and STORAGE_BACKEND (alternative name)
    storage_type = os.getenv("STORAGE_TYPE", os.getenv("STORAGE_BACKEND", "local")).lower()

    if storage_type == "r2":
        # Cloudflare R2 is S3-compatible. Wrap the S3 adapter with the R2
        # endpoint convention. Required env:
        #   R2_ACCOUNT_ID                — your Cloudflare account id
        #   R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY  — R2 API token
        #   R2_BUCKET_NAME                — R2 bucket
        #   R2_PUBLIC_DOMAIN              — public CDN host (e.g. media.clipsmith.app)
        logger.info("Initializing Cloudflare R2 storage adapter")
        account_id = os.getenv("R2_ACCOUNT_ID")
        access_key = os.getenv("R2_ACCESS_KEY_ID")
        secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
        bucket = os.getenv("R2_BUCKET_NAME")
        public_domain = os.getenv("R2_PUBLIC_DOMAIN")
        missing = [
            n
            for n, v in [
                ("R2_ACCOUNT_ID", account_id),
                ("R2_ACCESS_KEY_ID", access_key),
                ("R2_SECRET_ACCESS_KEY", secret_key),
                ("R2_BUCKET_NAME", bucket),
            ]
            if not v
        ]
        if missing:
            raise ValueError(f"Missing R2 environment variables: {missing}")
        return S3StorageAdapter(
            bucket_name=bucket,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            aws_region="auto",  # R2 ignores region; "auto" is canonical
            cloudfront_domain=public_domain,
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        )

    if storage_type == "s3":
        logger.info("Initializing S3 storage adapter")

        required_env_vars = [
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "S3_BUCKET_NAME",
        ]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]

        if missing_vars:
            # Also check AWS_BUCKET_NAME as an alternative
            if "S3_BUCKET_NAME" in missing_vars and os.getenv("AWS_BUCKET_NAME"):
                missing_vars.remove("S3_BUCKET_NAME")
            if missing_vars:
                logger.error(f"Missing required S3 environment variables: {missing_vars}")
                raise ValueError(f"Missing environment variables: {missing_vars}")

        bucket_name = os.getenv("S3_BUCKET_NAME") or os.getenv("AWS_BUCKET_NAME")

        return S3StorageAdapter(
            bucket_name=bucket_name,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
            cloudfront_domain=os.getenv("CLOUDFRONT_DOMAIN"),
            endpoint_url=os.getenv(
                "AWS_ENDPOINT_URL"
            ),  # For testing with localstack/minio
        )

    elif storage_type == "gcs":
        logger.info("Initializing GCS storage adapter")

        from .gcs_storage_adapter import GCSStorageAdapter

        bucket_name = os.getenv("GCS_BUCKET_NAME")
        if not bucket_name:
            logger.error("Missing required GCS_BUCKET_NAME environment variable")
            raise ValueError("Missing environment variable: GCS_BUCKET_NAME")

        return GCSStorageAdapter(
            bucket_name=bucket_name,
            project_id=os.getenv("GCS_PROJECT_ID"),
            credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            cdn_domain=os.getenv("GCS_CDN_DOMAIN"),
        )

    elif storage_type == "local":
        logger.info("Initializing local filesystem storage adapter")
        base_url = os.getenv("STORAGE_BASE_URL", "http://localhost:8000/uploads")
        return FileSystemStorageAdapter(base_url=base_url)

    else:
        logger.error(
            f"Unknown storage type: {storage_type}. Supported types: 'local', 's3', 'r2', 'gcs'"
        )
        raise ValueError(f"Unsupported storage type: {storage_type}")


# Singleton instance for the application
storage_adapter: Union[StoragePort, None] = None


def get_storage_adapter() -> StoragePort:
    """Get the singleton storage adapter instance."""
    global storage_adapter
    if storage_adapter is None:
        storage_adapter = create_storage_adapter()
    return storage_adapter
