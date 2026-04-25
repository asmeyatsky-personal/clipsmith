"""Device token registration endpoints."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from ...domain.ports.push_port import DeviceToken, DeviceTokenRepositoryPort
from ..dependencies import get_current_user, get_device_token_repo

router = APIRouter(prefix="/push", tags=["push"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_token(
    body: dict,
    current_user=Depends(get_current_user),
    repo: DeviceTokenRepositoryPort = Depends(get_device_token_repo),
):
    token = (body or {}).get("token", "").strip()
    platform = (body or {}).get("platform", "ios")
    if not token:
        raise HTTPException(status_code=400, detail="token is required")
    if platform not in ("ios", "android", "web"):
        raise HTTPException(status_code=400, detail="invalid platform")
    repo.upsert(
        DeviceToken(
            token=token,
            user_id=current_user.id,
            platform=platform,
        )
    )
    return {"success": True}


@router.delete("/register/{token}", status_code=status.HTTP_204_NO_CONTENT)
def unregister_token(
    token: str,
    current_user=Depends(get_current_user),
    repo: DeviceTokenRepositoryPort = Depends(get_device_token_repo),
):
    repo.remove(token)
    return None
