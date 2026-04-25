"""Speech-to-text / captions generation port.

Application use cases depend on this; AssemblyAI / Whisper adapters live in
infrastructure.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class TranscriptWord:
    text: str
    start_seconds: float
    end_seconds: float


@dataclass(frozen=True)
class TranscriptionResult:
    full_text: str
    words: list[TranscriptWord]
    language: str | None = None


class TranscriptionPort(ABC):
    @abstractmethod
    def transcribe(self, audio_file_path: str) -> TranscriptionResult: ...
