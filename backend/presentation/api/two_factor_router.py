"""Standalone 2FA router (alongside `/auth/2fa/*` endpoints in auth_router).

Kept for backwards compatibility with frontend clients hitting `/api/auth/2fa/*`.
All endpoints delegate to the same application use cases.
"""
from fastapi import APIRouter, Depends, HTTPException

from ...application.use_cases.manage_2fa import (
    DisableTwoFactorUseCase,
    GetTwoFactorStatusUseCase,
    SetupTwoFactorUseCase,
    VerifyTwoFactorSetupUseCase,
)
from ..dependencies import (
    get_2fa_disable_use_case,
    get_2fa_setup_use_case,
    get_2fa_status_use_case,
    get_2fa_verify_use_case,
    get_current_user,
)

router = APIRouter(prefix="/api/auth/2fa", tags=["two-factor-auth"])


@router.post("/setup")
def setup_2fa(
    current_user=Depends(get_current_user),
    use_case: SetupTwoFactorUseCase = Depends(get_2fa_setup_use_case),
):
    try:
        result = use_case.execute(
            user_id=current_user.id, email=current_user.email, method="totp"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "success": True,
        "secret": result.secret,
        "qr_code": f"data:image/png;base64,{result.qr_code_b64}",
        "backup_codes": result.backup_codes,
        "message": "Save these backup codes! They won't be shown again.",
    }


@router.post("/verify")
def verify_2fa(
    request_body: dict,
    current_user=Depends(get_current_user),
    use_case: VerifyTwoFactorSetupUseCase = Depends(get_2fa_verify_use_case),
):
    code = request_body.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="code is required")
    try:
        ok = use_case.execute(current_user.id, code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    return {"success": True, "message": "2FA enabled successfully"}


@router.post("/disable")
def disable_2fa(
    request_body: dict,
    current_user=Depends(get_current_user),
    use_case: DisableTwoFactorUseCase = Depends(get_2fa_disable_use_case),
):
    password = request_body.get("password") or request_body.get("code")
    if not password:
        raise HTTPException(status_code=400, detail="password is required")
    try:
        use_case.execute(current_user.id, password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True, "message": "2FA disabled successfully"}


@router.get("/status")
def get_2fa_status(
    current_user=Depends(get_current_user),
    use_case: GetTwoFactorStatusUseCase = Depends(get_2fa_status_use_case),
):
    s = use_case.execute(current_user.id)
    return {"success": True, "enabled": s.enabled, "method": s.method}
