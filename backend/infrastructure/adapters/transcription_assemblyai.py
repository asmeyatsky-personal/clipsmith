"""AssemblyAI implementation of TranscriptionPort."""
from __future__ import annotations

import logging
import os

from backend.application.utils.resilience import assemblyai_breaker
from backend.domain.ports.transcription_port import (
    TranscriptionPort,
    TranscriptionResult,
    TranscriptWord,
)

logger = logging.getLogger(__name__)


class AssemblyAITranscriber(TranscriptionPort):
    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or os.getenv("ASSEMBLYAI_API_KEY")
        if not self._api_key:
            raise ValueError("ASSEMBLYAI_API_KEY not configured")

    def transcribe(self, audio_file_path: str) -> TranscriptionResult:
        import assemblyai as aai

        aai.settings.api_key = self._api_key
        transcriber = aai.Transcriber()
        config = aai.TranscriptionConfig(
            word_boost=["clipsmith", "video", "editing"],
        )
        logger.info("Starting AssemblyAI transcription: %s", audio_file_path)
        transcript = assemblyai_breaker.call(
            transcriber.transcribe, audio_file_path, config=config
        )
        if transcript.status == aai.TranscriptStatus.error:
            raise RuntimeError(f"AssemblyAI failed: {transcript.error}")

        words = [
            TranscriptWord(
                text=w.text,
                start_seconds=w.start / 1000.0,
                end_seconds=w.end / 1000.0,
            )
            for w in (transcript.words or [])
        ]
        return TranscriptionResult(
            full_text=transcript.text or "",
            words=words,
            language=getattr(transcript, "language_code", None),
        )


class PlaceholderTranscriber(TranscriptionPort):
    """Dev-mode transcriber. Probes audio duration and emits a fixed set
    of placeholder caption rows so the rest of the pipeline (UI, tests)
    has something to render without an AssemblyAI key."""

    _SAMPLES = (
        "(transcription disabled in dev)",
        "Set ASSEMBLYAI_API_KEY to enable real captions.",
        "Or wire a Whisper adapter via TranscriptionPort.",
    )

    def transcribe(self, audio_file_path: str) -> TranscriptionResult:
        duration = 30.0
        try:
            import ffmpeg

            probe = ffmpeg.probe(audio_file_path)
            duration = float(probe.get("format", {}).get("duration", 30.0))
        except Exception:
            pass

        # Emit one TranscriptWord per sample so the use-case segmenter has
        # timing info to chunk by.
        seg = duration / max(len(self._SAMPLES), 1)
        words: list[TranscriptWord] = []
        for i, text in enumerate(self._SAMPLES):
            words.append(
                TranscriptWord(
                    text=text + ".",  # trigger sentence-terminator chunking
                    start_seconds=i * seg,
                    end_seconds=(i + 1) * seg,
                )
            )
        return TranscriptionResult(
            full_text=" ".join(self._SAMPLES),
            words=words,
            language="en",
        )


def get_transcriber() -> TranscriptionPort:
    """Factory: prefer AssemblyAI when configured, fall back to placeholder."""
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    env = os.getenv("ENVIRONMENT", "development")
    if not api_key or api_key in ("", "your-assemblyai-api-key"):
        if env == "production":
            raise ValueError("ASSEMBLYAI_API_KEY required in production")
        return PlaceholderTranscriber()
    return AssemblyAITranscriber(api_key)
