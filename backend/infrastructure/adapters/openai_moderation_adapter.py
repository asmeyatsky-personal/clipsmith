"""OpenAI Moderation API adapter — text classification for UGC pre-screen.

Free tier of OpenAI's /v1/moderations endpoint. Requires OPENAI_API_KEY.
NoopTextModerator is the dev fallback.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Iterable

from backend.application.utils.resilience import http_breaker
from backend.domain.ports.text_moderation_port import (
    ModerationVerdict,
    TextModerationPort,
)

logger = logging.getLogger(__name__)


class NoopTextModerator(TextModerationPort):
    """Dev fallback. Flags only the most obvious slur tokens for safety."""

    # Map blatant dev-mode tokens to OpenAI-equivalent categories so the
    # auto-reject pipeline behaves consistently with prod.
    _BLATANT_TOKENS: dict[str, str] = {
        "child porn": "sexual/minors",
        "csam": "sexual/minors",
        "kill yourself": "self-harm/instructions",
        "shoot up": "violence/graphic",
    }

    def classify(self, text: str) -> ModerationVerdict:
        lowered = (text or "").lower()
        for token, category in self._BLATANT_TOKENS.items():
            if token in lowered:
                return ModerationVerdict(
                    flagged=True, score=0.99, reasons=(category,)
                )
        return ModerationVerdict(flagged=False, score=0.0, reasons=())


class OpenAIModeratorAdapter(TextModerationPort):
    """OpenAI /v1/moderations — free tier, low-latency.

    Returns ModerationVerdict(flagged, score, reasons) where reasons is
    the OpenAI category names whose score exceeds the global threshold.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "omni-moderation-latest",
        threshold: float = 0.5,
    ):
        self._api_key = api_key
        self._model = model
        self._threshold = threshold

    def classify(self, text: str) -> ModerationVerdict:
        if not text or not text.strip():
            return ModerationVerdict(flagged=False, score=0.0, reasons=())

        import httpx

        body = {"model": self._model, "input": text[:32_000]}
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = http_breaker.call(
                httpx.post,
                "https://api.openai.com/v1/moderations",
                headers=headers,
                content=json.dumps(body),
                timeout=10.0,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as e:
            logger.warning("OpenAI moderation call failed: %s — falling open", e)
            return ModerationVerdict(flagged=False, score=0.0, reasons=())

        result = payload.get("results", [{}])[0]
        flagged = bool(result.get("flagged", False))
        category_scores = result.get("category_scores", {}) or {}
        max_score = max(category_scores.values(), default=0.0)
        reasons = tuple(
            cat for cat, score in category_scores.items() if score >= self._threshold
        )
        return ModerationVerdict(flagged=flagged, score=float(max_score), reasons=reasons)


def get_text_moderator() -> TextModerationPort:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return NoopTextModerator()
    return OpenAIModeratorAdapter(api_key=api_key)
