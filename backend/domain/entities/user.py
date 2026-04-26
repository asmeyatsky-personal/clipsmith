from dataclasses import dataclass, replace
from typing import Optional

from ..base import Entity


@dataclass(frozen=True, kw_only=True)
class User(Entity):
    username: str
    email: str
    hashed_password: str = ""
    is_active: bool = True
    bio: str = ""
    avatar_url: Optional[str] = None

    def with_profile_update(
        self,
        *,
        bio: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> "User":
        return replace(
            self,
            bio=bio if bio is not None else self.bio,
            avatar_url=avatar_url if avatar_url is not None else self.avatar_url,
        )
