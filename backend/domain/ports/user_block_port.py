"""User block port for Apple Guideline 1.2 compliance."""
from abc import ABC, abstractmethod


class UserBlockRepositoryPort(ABC):
    @abstractmethod
    def block(self, blocker_id: str, blocked_id: str) -> None: ...

    @abstractmethod
    def unblock(self, blocker_id: str, blocked_id: str) -> None: ...

    @abstractmethod
    def is_blocked(self, blocker_id: str, blocked_id: str) -> bool: ...

    @abstractmethod
    def list_blocked_ids(self, blocker_id: str) -> list[str]: ...

    @abstractmethod
    def list_blockers_of(self, blocked_id: str) -> list[str]: ...
