"""Caption generation use case.

Pure application layer: depends only on domain ports. The actual
transcription happens in an adapter that implements TranscriptionPort
(AssemblyAITranscriber, future WhisperTranscriber, PlaceholderTranscriber).
"""
from __future__ import annotations

import logging
from typing import List

from ...domain.entities.caption import Caption
from ...domain.ports.repository_ports import CaptionRepositoryPort, VideoRepositoryPort
from ...domain.ports.transcription_port import (
    TranscriptionPort,
    TranscriptionResult,
    TranscriptWord,
)
from ..dtos.caption_dto import CaptionResponseDTO

logger = logging.getLogger(__name__)


def _segment_words(words: list[TranscriptWord], video_id: str) -> list[Caption]:
    """Group words into ~5-word caption rows, respecting sentence terminators."""
    captions: list[Caption] = []
    if not words:
        return captions

    current_text = ""
    current_start = 0.0
    last_end = 0.0
    for w in words:
        if not current_text:
            current_start = w.start_seconds
        current_text += w.text + " "
        last_end = w.end_seconds
        end_of_thought = w.text.endswith((".", "!", "?"))
        if len(current_text.split()) >= 5 or end_of_thought:
            captions.append(
                Caption(
                    video_id=video_id,
                    text=current_text.strip(),
                    start_time=round(current_start, 3),
                    end_time=round(last_end, 3),
                    language="en",
                )
            )
            current_text = ""
    if current_text:
        captions.append(
            Caption(
                video_id=video_id,
                text=current_text.strip(),
                start_time=round(current_start, 3),
                end_time=round(last_end, 3),
                language="en",
            )
        )
    return captions


class GenerateCaptionsUseCase:
    def __init__(
        self,
        video_repo: VideoRepositoryPort,
        caption_repo: CaptionRepositoryPort,
        transcriber: TranscriptionPort,
    ):
        self._video_repo = video_repo
        self._caption_repo = caption_repo
        self._transcriber = transcriber

    def execute(self, video_id: str, audio_file_path: str) -> List[CaptionResponseDTO]:
        video = self._video_repo.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video with ID {video_id} not found.")

        result: TranscriptionResult = self._transcriber.transcribe(audio_file_path)

        captions = _segment_words(list(result.words), video_id)

        # If the transcriber returned plain text only, treat it as one row.
        if not captions and result.full_text.strip():
            captions = [
                Caption(
                    video_id=video_id,
                    text=result.full_text.strip(),
                    start_time=0.0,
                    end_time=30.0,
                    language=result.language or "en",
                )
            ]

        saved_dtos: list[CaptionResponseDTO] = []
        for c in captions:
            saved = self._caption_repo.save(c)
            saved_dtos.append(
                CaptionResponseDTO(
                    id=saved.id,
                    video_id=saved.video_id,
                    text=saved.text,
                    start_time=saved.start_time,
                    end_time=saved.end_time,
                    language=saved.language,
                )
            )
        logger.info("Generated %d captions for video %s", len(saved_dtos), video_id)
        return saved_dtos
