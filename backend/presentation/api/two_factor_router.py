"""Standalone 2FA router (alongside `/auth/2fa/*` endpoints in auth_router).

Kept for backwards compatibility with frontend clients hitting `/api/auth/2fa/*`.
All endpoints delegate to the same application use cases.
"""
from fastapi import APIRouter, Depends, HTTPException

from ...application.use_cases.manage_2fa import (
    GetTwoFactorStatusUseCase,
    SetupTwoFactorUseCase,
    VerifyTwoFactorSetupUseCase,
)
from sqlmodel import Session, select

from ..dependencies import (
    db_models,
    get_2fa_setup_use_case,
    get_2fa_status_use_case,
    get_2fa_verify_use_case,
    get_current_user,
    get_session_for_router as get_session,
    get_two_factor_repo,
    get_two_factor_service,
)

TwoFactorSecretDB = db_models.TwoFactorSecretDB

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
    repo=Depends(get_two_factor_repo),
    service=Depends(get_two_factor_service),
):
    """Disable 2FA by verifying a current TOTP code (legacy contract)."""
    code = request_body.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="code is required")

    active = repo.get_active(current_user.id)
    if not active:
        raise HTTPException(status_code=400, detail="2FA is not enabled")
    if not service.verify_totp_code(active.secret, code):
        raise HTTPException(status_code=400, detail="Invalid verification code")
    repo.delete_all_for_user(current_user.id)
    return {"success": True, "message": "2FA disabled successfully"}


@router.get("/status")
def get_2fa_status(
    current_user=Depends(get_current_user),
    use_case: GetTwoFactorStatusUseCase = Depends(get_2fa_status_use_case),
):
    s = use_case.execute(current_user.id)
    return {"success": True, "enabled": s.enabled, "method": s.method}


@router.post("/backup-codes/verify")
def verify_backup_code(
    request_body: dict,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Verify a backup code for 2FA recovery."""
    code = request_body.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="code is required")

    active_secret = session.exec(
        select(TwoFactorSecretDB).where(
            TwoFactorSecretDB.user_id == current_user.id,
            TwoFactorSecretDB.is_active == True,  # noqa: E712
        )
    ).first()

    if not active_secret:
        raise HTTPException(status_code=400, detail="2FA is not enabled")

    backup_codes = (
        active_secret.backup_codes.split(",") if active_secret.backup_codes else []
    )
    if code not in backup_codes:
        raise HTTPException(status_code=400, detail="Invalid backup code")

    backup_codes.remove(code)
    active_secret.backup_codes = ",".join(backup_codes)
    session.add(active_secret)
    session.commit()

    return {
        "success": True,
        "message": "Backup code verified successfully",
        "remaining_codes": len(backup_codes),
    }
