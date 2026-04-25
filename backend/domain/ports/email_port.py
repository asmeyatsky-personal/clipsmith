from abc import ABC, abstractmethod


class EmailSenderPort(ABC):
    @abstractmethod
    def send(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: str | None = None,
    ) -> bool: ...
