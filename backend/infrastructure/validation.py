import re
import bleach
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated


ALLOWED_TAGS = [
    "b",
    "i",
    "u",
    "em",
    "strong",
    "a",
    "p",
    "br",
    "span",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "blockquote",
    "code",
    "pre",
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "rel"],
    "span": ["class"],
    "*": ["class", "id"],
}

MAX_USERNAME_LENGTH = 30
MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 5000
MAX_COMMENT_LENGTH = 1000


def sanitize_html(text: str) -> str:
    return bleach.clean(
        text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True
    )


def sanitize_filename(filename: str) -> str:
    sanitized = re.sub(r"[^\w\s.-]", "", filename)
    sanitized = re.sub(r"\s+", "_", sanitized)
    return sanitized[:255]


def validate_username(username: str) -> str:
    if not username or len(username) < 3:
        raise ValueError("Username must be at least 3 characters")
    if len(username) > MAX_USERNAME_LENGTH:
        raise ValueError(f"Username must be at most {MAX_USERNAME_LENGTH} characters")
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        raise ValueError(
            "Username can only contain letters, numbers, underscores, and hyphens"
        )
    return username.lower()


def validate_email(email: str) -> str:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email, re.IGNORECASE):
        raise ValueError("Invalid email format")
    return email.lower()


def validate_url(url: str) -> str:
    pattern = r"^https?://"
    if not re.match(pattern, url, re.IGNORECASE):
        raise ValueError("URL must start with http:// or https://")
    if len(url) > 2048:
        raise ValueError("URL too long")
    return url


def validate_hashtag(hashtag: str) -> str:
    cleaned = re.sub(r"[^\w]", "", hashtag)
    if len(cleaned) < 2:
        raise ValueError("Hashtag must be at least 2 characters")
    if len(cleaned) > 100:
        raise ValueError("Hashtag too long")
    return cleaned.lower()


def validate_uuid(value: str) -> str:
    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    if not re.match(uuid_pattern, value, re.IGNORECASE):
        raise ValueError("Invalid UUID format")
    return value


def validate_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    if len(password) > 128:
        raise ValueError("Password too long")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"[0-9]", password):
        raise ValueError("Password must contain at least one digit")
    return password


class SanitizedStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info=None):
        if isinstance(v, str):
            return cls(sanitize_html(v.strip()))
        raise ValueError("Must be a string")


class UsernameField(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info=None):
        if isinstance(v, str):
            return cls(validate_username(v))
        raise ValueError("Must be a string")


class EmailField(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info=None):
        if isinstance(v, str):
            return cls(validate_email(v))
        raise ValueError("Must be a string")


class TitleField(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info=None):
        if isinstance(v, str):
            stripped = v.strip()
            if len(stripped) < 1:
                raise ValueError("Title cannot be empty")
            if len(stripped) > MAX_TITLE_LENGTH:
                raise ValueError(f"Title must be at most {MAX_TITLE_LENGTH} characters")
            return cls(sanitize_html(stripped))
        raise ValueError("Must be a string")


class DescriptionField(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info=None):
        if isinstance(v, str):
            stripped = v.strip()
            if len(stripped) > MAX_DESCRIPTION_LENGTH:
                raise ValueError(
                    f"Description must be at most {MAX_DESCRIPTION_LENGTH} characters"
                )
            return cls(sanitize_html(stripped))
        raise ValueError("Must be a string")


class CommentField(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info=None):
        if isinstance(v, str):
            stripped = v.strip()
            if len(stripped) < 1:
                raise ValueError("Comment cannot be empty")
            if len(stripped) > MAX_COMMENT_LENGTH:
                raise ValueError(
                    f"Comment must be at most {MAX_COMMENT_LENGTH} characters"
                )
            return cls(sanitize_html(stripped))
        raise ValueError("Must be a string")


class UUIDField(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info=None):
        if isinstance(v, str):
            return cls(validate_uuid(v))
        raise ValueError("Must be a string")


class ValidatedUserRegistration(BaseModel):
    username: Annotated[str, BeforeValidator(UsernameField.validate)]
    email: Annotated[str, BeforeValidator(EmailField.validate)]
    password: Annotated[str, BeforeValidator(validate_password)]


class ValidatedVideoUpload(BaseModel):
    title: Annotated[str, BeforeValidator(TitleField.validate)]
    description: Annotated[str, BeforeValidator(DescriptionField.validate)]


class ValidatedComment(BaseModel):
    content: Annotated[str, BeforeValidator(CommentField.validate)]


class ValidatedHashtag(BaseModel):
    name: Annotated[str, BeforeValidator(validate_hashtag)]
