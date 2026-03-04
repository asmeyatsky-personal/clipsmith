from fastapi import APIRouter, Depends, HTTPException, status
from ...infrastructure.repositories.database import get_session
from .auth_router import get_current_user
from ...application.services.two_factor_service import TwoFactorService
from sqlmodel import Session, select

router = APIRouter(prefix="/api/auth/2fa", tags=["two-factor-auth"])


def get_two_factor_service() -> TwoFactorService:
    """Dependency injection for TwoFactorService."""
    return TwoFactorService(user_repo=None)


# ==================== 2FA Setup ====================


@router.post("/setup")
def setup_2fa(
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
    two_factor_service: TwoFactorService = Depends(get_two_factor_service),
):
    """Setup 2FA for the current user. Returns QR code and backup codes."""
    from ...infrastructure.repositories.models import TwoFactorSecretDB

    # Check if 2FA is already enabled
    existing = session.exec(
        select(TwoFactorSecretDB).where(
            TwoFactorSecretDB.user_id == current_user.id,
            TwoFactorSecretDB.is_active == True,
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=400, detail="2FA is already enabled. Disable it first."
        )

    try:
        secret, qr_code, backup_codes = two_factor_service.setup_2fa(
            user_id=current_user.id,
            method="totp",
            email=current_user.email,
        )

        # Store the secret as inactive until verified
        temp_secret = TwoFactorSecretDB(
            user_id=current_user.id,
            method="totp",
            secret=secret,
            backup_codes=",".join(backup_codes),
            is_active=False,
        )
        session.add(temp_secret)
        session.commit()

        return {
            "success": True,
            "secret": secret,
            "qr_code": f"data:image/png;base64,{qr_code}",
            "backup_codes": backup_codes,
            "message": "Save these backup codes! They won't be shown again.",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== 2FA Verification ====================


@router.post("/verify")
def verify_2fa(
    request_body: dict,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
    two_factor_service: TwoFactorService = Depends(get_two_factor_service),
):
    """Verify a TOTP code to activate 2FA setup."""
    from ...infrastructure.repositories.models import TwoFactorSecretDB

    code = request_body.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="code is required")

    # Find the pending (inactive) secret
    statement = select(TwoFactorSecretDB).where(
        TwoFactorSecretDB.user_id == current_user.id,
        TwoFactorSecretDB.is_active == False,
    )
    temp_secret = session.exec(statement).first()

    if not temp_secret:
        raise HTTPException(
            status_code=400, detail="No pending 2FA setup. Start setup first."
        )

    if two_factor_service.verify_totp_code(temp_secret.secret, code):
        temp_secret.is_active = True
        session.add(temp_secret)
        session.commit()
        return {"success": True, "message": "2FA enabled successfully"}

    raise HTTPException(status_code=400, detail="Invalid verification code")


# ==================== 2FA Disable ====================


@router.post("/disable")
def disable_2fa(
    request_body: dict,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
    two_factor_service: TwoFactorService = Depends(get_two_factor_service),
):
    """Disable 2FA after verifying with a current TOTP code."""
    from ...infrastructure.repositories.models import TwoFactorSecretDB

    code = request_body.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="code is required")

    # Find the active secret
    active_secret = session.exec(
        select(TwoFactorSecretDB).where(
            TwoFactorSecretDB.user_id == current_user.id,
            TwoFactorSecretDB.is_active == True,
        )
    ).first()

    if not active_secret:
        raise HTTPException(status_code=400, detail="2FA is not enabled")

    # Verify the code before disabling
    if not two_factor_service.verify_totp_code(active_secret.secret, code):
        raise HTTPException(status_code=400, detail="Invalid verification code")

    # Delete all 2FA records for this user
    all_secrets = session.exec(
        select(TwoFactorSecretDB).where(
            TwoFactorSecretDB.user_id == current_user.id
        )
    ).all()

    for secret in all_secrets:
        session.delete(secret)

    session.commit()

    return {"success": True, "message": "2FA disabled successfully"}


# ==================== 2FA Status ====================


@router.get("/status")
def get_2fa_status(
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Check whether 2FA is enabled for the current user."""
    from ...infrastructure.repositories.models import TwoFactorSecretDB

    secret = session.exec(
        select(TwoFactorSecretDB).where(
            TwoFactorSecretDB.user_id == current_user.id,
            TwoFactorSecretDB.is_active == True,
        )
    ).first()

    if not secret:
        return {"success": True, "enabled": False, "method": None}

    return {"success": True, "enabled": True, "method": secret.method}


# ==================== Backup Code Verification ====================


@router.post("/backup-codes/verify")
def verify_backup_code(
    request_body: dict,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Verify a backup code for 2FA recovery."""
    from ...infrastructure.repositories.models import TwoFactorSecretDB

    code = request_body.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="code is required")

    active_secret = session.exec(
        select(TwoFactorSecretDB).where(
            TwoFactorSecretDB.user_id == current_user.id,
            TwoFactorSecretDB.is_active == True,
        )
    ).first()

    if not active_secret:
        raise HTTPException(status_code=400, detail="2FA is not enabled")

    # Check if the code is in the backup codes list
    backup_codes = active_secret.backup_codes.split(",") if active_secret.backup_codes else []

    if code not in backup_codes:
        raise HTTPException(status_code=400, detail="Invalid backup code")

    # Remove the used backup code
    backup_codes.remove(code)
    active_secret.backup_codes = ",".join(backup_codes)
    session.add(active_secret)
    session.commit()

    return {
        "success": True,
        "message": "Backup code verified successfully",
        "remaining_codes": len(backup_codes),
    }
