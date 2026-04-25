"""Text moderation port — pre-screen titles, descriptions, comments.

Adapter implementations: OpenAI Moderation, Perspective API, Hive AI, etc.
A NoopAdapter exists for dev/test where no API key is configured.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ModerationVerdict:
    flagged: bool
    score: float  # 0.0–1.0 confidence the content is violating
    reasons: tuple[str, ...]  # category labels e.g. ("violence", "harassment")


class TextModerationPort(ABC):
    @abstractmethod
    def classify(self, text: str) -> ModerationVerdict: ...
