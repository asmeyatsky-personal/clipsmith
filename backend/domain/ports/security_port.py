from abc import ABC, abstractmethod


class PasswordHelperPort(ABC):
    @abstractmethod
    def hash(self, password: str) -> str: ...

    @abstractmethod
    def verify(self, plain: str, hashed: str) -> bool: ...


class JWTPort(ABC):
    @abstractmethod
    def encode(self, claims: dict, expires_in_seconds: int) -> str: ...

    @abstractmethod
    def decode(self, token: str) -> dict: ...
