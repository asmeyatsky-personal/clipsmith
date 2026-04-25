"""Push notification ports.

DeviceTokenRepositoryPort persists tokens; PushSenderPort dispatches.
APNs implementation requires a key from App Store Connect — kept abstract
here so an APNs/FCM/web-push adapter can be wired in infrastructure later.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class DeviceToken:
    token: str
    user_id: str
    platform: str  # "ios" | "android" | "web"


@dataclass(frozen=True)
class PushPayload:
    title: str
    body: str
    data: dict | None = None  # custom routing payload
    badge: int | None = None


class DeviceTokenRepositoryPort(ABC):
    @abstractmethod
    def upsert(self, token: DeviceToken) -> None: ...

    @abstractmethod
    def remove(self, token: str) -> None: ...

    @abstractmethod
    def list_for_user(self, user_id: str) -> list[DeviceToken]: ...

    @abstractmethod
    def list_for_users(self, user_ids: Iterable[str]) -> list[DeviceToken]: ...


class PushSenderPort(ABC):
    @abstractmethod
    def send(self, tokens: Iterable[str], payload: PushPayload) -> None: ...
