from datetime import date, datetime
from pydantic import BaseModel, EmailStr, field_validator
from ..utils.sanitization import sanitize_input, MAX_USERNAME_LENGTH

# Apple Guideline 1.3 + COPPA + GDPR: minimum age is 13 globally, 16 in EEA.
# We enforce 13 here and surface a stricter regional gate at the client.
_MIN_AGE_YEARS = 13


class RegisterRequestDTO(BaseModel):
    username: str
    email: EmailStr
    password: str
    date_of_birth: date  # required — see _MIN_AGE_YEARS

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")
        if len(v) > MAX_USERNAME_LENGTH:
            raise ValueError(f"Username cannot exceed {MAX_USERNAME_LENGTH} characters")
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return sanitize_input(v.strip())

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: date) -> date:
        today = datetime.utcnow().date()
        if v >= today:
            raise ValueError("Date of birth must be in the past")
        # Compute age (calendar years, accounting for not-yet-this-year birthday).
        age = today.year - v.year - (
            (today.month, today.day) < (v.month, v.day)
        )
        if age < _MIN_AGE_YEARS:
            raise ValueError(
                f"You must be at least {_MIN_AGE_YEARS} years old to use Clipsmith"
            )
        return v


class LoginRequestDTO(BaseModel):
    email: EmailStr
    password: str


class TokenResponseDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponseDTO(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool


class LoginResponseDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponseDTO


class PasswordResetRequestDTO(BaseModel):
    email: EmailStr


class PasswordResetConfirmDTO(BaseModel):
    token: str
    new_password: str
