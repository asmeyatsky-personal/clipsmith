import os

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from slowapi import Limiter
from slowapi.util import get_remote_address

from ...application.dtos.auth_dto import (
    LoginRequestDTO,
    LoginResponseDTO,
    PasswordResetConfirmDTO,
    PasswordResetRequestDTO,
    RegisterRequestDTO,
    UserResponseDTO,
)
from ...application.use_cases.authenticate_user import AuthenticateUserUseCase
from ...application.use_cases.manage_2fa import (
    DisableTwoFactorUseCase,
    GetTwoFactorStatusUseCase,
    SetupTwoFactorUseCase,
    VerifyLoginTwoFactorUseCase,
    VerifyTwoFactorSetupUseCase,
)
from ...application.use_cases.password_reset import (
    ConfirmPasswordResetUseCase,
    RequestPasswordResetUseCase,
)
from ...application.use_cases.email_verification import (
    ConfirmEmailVerificationUseCase,
    RequestEmailVerificationUseCase,
)
from ...application.use_cases.register_user import RegisterUserUseCase
from ..dependencies import (
    get_2fa_disable_use_case,
    get_2fa_login_verify_use_case,
    get_2fa_setup_use_case,
    get_2fa_status_use_case,
    get_2fa_verify_use_case,
    get_authenticate_use_case,
    get_confirm_password_reset_use_case,
    get_current_user,  # re-exported for legacy callers (analytics_router, moderation_router, etc.)
    get_email_service,
    get_register_use_case,
    get_request_password_reset_use_case,
    get_session_for_router,
    get_user_repo,
)

# Backwards-compat: routers historically did `from .auth_router import get_current_user`
__all__ = ["router", "get_current_user", "limiter"]

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# --- Email verification (A2) ---


@router.post("/verify-email/request")
def request_email_verification(
    current_user=Depends(get_current_user),
    user_repo=Depends(get_user_repo),
    email_sender=Depends(get_email_service),
    session=Depends(get_session_for_router),
):
    use_case = RequestEmailVerificationUseCase(user_repo, email_sender, session)
    try:
        use_case.execute(current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"success": True, "message": "Verification email sent"}


@router.post("/verify-email/{token}")
def confirm_email_verification(
    token: str,
    session=Depends(get_session_for_router),
):
    use_case = ConfirmEmailVerificationUseCase(session)
    if not use_case.execute(token):
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"success": True, "message": "Email verified"}


@router.post(
    "/register", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/minute")
def register(
    request: Request,
    dto: RegisterRequestDTO,
    use_case: RegisterUserUseCase = Depends(get_register_use_case),
):
    try:
        return use_case.execute(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=LoginResponseDTO)
@limiter.limit("10/minute")
def login(
    request: Request,
    response: Response,
    dto: LoginRequestDTO,
    use_case: AuthenticateUserUseCase = Depends(get_authenticate_use_case),
):
    result = use_case.execute(dto)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    response.set_cookie(
        key="access_token",
        value=result.access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=30 * 60,
    )
    return result


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}


@router.get("/apple/start")
def apple_signin_start():
    """Sign in with Apple — redirect kick-off.

    Production wiring requires an Apple Services ID, key, and team ID.
    For Capacitor builds the iOS shell intercepts this URL and opens
    ASAuthorizationAppleIDProvider natively. For the web build we'll
    redirect to Apple's authorize endpoint once the env vars are set.
    Until then, this endpoint surfaces a 503 with guidance so the UI
    button is clickable and we don't ship a silent failure.
    """
    services_id = os.getenv("APPLE_SERVICES_ID")
    if not services_id:
        raise HTTPException(
            status_code=503,
            detail="Apple Sign-In not yet configured. Set APPLE_SERVICES_ID, APPLE_TEAM_ID, APPLE_KEY_ID, APPLE_PRIVATE_KEY.",
        )
    return {"redirect": f"https://appleid.apple.com/auth/authorize?client_id={services_id}&response_type=code&scope=email%20name&response_mode=form_post"}


@router.post("/apple/callback")
def apple_signin_callback(code: str = Form(...), id_token: str | None = Form(default=None)):
    """Sign in with Apple — token-exchange callback.

    Real implementation verifies the id_token JWT against Apple's JWKS,
    upserts a User by Apple's stable `sub`, and returns our own JWT.
    Scaffolded for Phase 1.5 native plumbing per phase1_5_appstore.md §2.
    """
    raise HTTPException(
        status_code=501,
        detail="Sign-In-with-Apple callback is scaffolded; full token verify ships with Phase 1.5.",
    )


@router.get("/me", response_model=UserResponseDTO)
def get_me(current_user=Depends(get_current_user)):
    return UserResponseDTO(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
    )


_GENERIC_RESET_REPLY = {
    "message": "If an account with that email exists, a password reset link has been sent."
}


@router.post("/password-reset/request")
@limiter.limit("2/minute")
def request_password_reset(
    request: Request,
    dto: PasswordResetRequestDTO,
    use_case: RequestPasswordResetUseCase = Depends(get_request_password_reset_use_case),
):
    use_case.execute(dto.email)
    return _GENERIC_RESET_REPLY


@router.post("/password-reset/confirm")
@limiter.limit("5/minute")
def confirm_password_reset(
    request: Request,
    dto: PasswordResetConfirmDTO,
    use_case: ConfirmPasswordResetUseCase = Depends(get_confirm_password_reset_use_case),
):
    try:
        use_case.execute(dto.token, dto.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Password has been reset successfully"}


@router.get("/2fa/status", response_model=dict)
def get_2fa_status(
    current_user=Depends(get_current_user),
    use_case: GetTwoFactorStatusUseCase = Depends(get_2fa_status_use_case),
):
    status_result = use_case.execute(current_user.id)
    return {"enabled": status_result.enabled, "method": status_result.method}


@router.post("/2fa/setup")
def setup_2fa(
    request: Request,
    method: str = "totp",
    current_user=Depends(get_current_user),
    use_case: SetupTwoFactorUseCase = Depends(get_2fa_setup_use_case),
):
    try:
        result = use_case.execute(
            user_id=current_user.id, email=current_user.email, method=method
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "secret": result.secret,
        "qr_code": f"data:image/png;base64,{result.qr_code_b64}",
        "backup_codes": result.backup_codes,
        "message": "Save these backup codes! They won't be shown again.",
    }


@router.post("/2fa/verify")
def verify_2fa(
    request: Request,
    code: str,
    current_user=Depends(get_current_user),
    use_case: VerifyTwoFactorSetupUseCase = Depends(get_2fa_verify_use_case),
):
    try:
        ok = use_case.execute(current_user.id, code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    return {"message": "2FA enabled successfully"}


@router.post("/2fa/disable")
def disable_2fa(
    request: Request,
    password: str,
    current_user=Depends(get_current_user),
    use_case: DisableTwoFactorUseCase = Depends(get_2fa_disable_use_case),
):
    try:
        use_case.execute(current_user.id, password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "2FA disabled successfully"}


@router.post("/2fa/login-verify")
def verify_2fa_login(
    request: Request,
    code: str,
    user_id: str,
    use_case: VerifyLoginTwoFactorUseCase = Depends(get_2fa_login_verify_use_case),
):
    if use_case.execute(user_id, code):
        return {"verified": True}
    return {"verified": False, "detail": "Invalid code"}
