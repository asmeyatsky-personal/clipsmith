"""APNs push sender. Requires APNS_KEY_PATH (.p8), APNS_KEY_ID,
APNS_TEAM_ID, and APNS_TOPIC (the iOS bundle id) at runtime.

Falls back to a NoopPushSender when not configured (dev mode).
"""
from __future__ import annotations

import logging
import os
from typing import Iterable

from backend.application.utils.resilience import http_breaker
from backend.domain.ports.push_port import PushPayload, PushSenderPort

logger = logging.getLogger(__name__)


class NoopPushSender(PushSenderPort):
    """Logs the payload but doesn't actually send. Used in dev/test."""

    def send(self, tokens: Iterable[str], payload: PushPayload) -> None:
        token_list = list(tokens)
        logger.info(
            "[NoopPushSender] would send to %d token(s): title=%r body=%r",
            len(token_list),
            payload.title,
            payload.body,
        )


class APNsPushSender(PushSenderPort):
    """Apple Push Notification service via the modern HTTP/2 + JWT API.

    We avoid pulling a heavy library; sender uses httpx with a JWT signed via
    the .p8 private key. Wraps each request in the http circuit breaker.
    """

    def __init__(
        self,
        key_path: str,
        key_id: str,
        team_id: str,
        topic: str,
        sandbox: bool = False,
    ):
        self._key_path = key_path
        self._key_id = key_id
        self._team_id = team_id
        self._topic = topic
        self._host = (
            "https://api.sandbox.push.apple.com"
            if sandbox
            else "https://api.push.apple.com"
        )

    def _jwt(self) -> str:
        # Lazy import — keeps optional in dev when these libs aren't installed.
        import time
        import jwt  # PyJWT
        from cryptography.hazmat.primitives.serialization import load_pem_private_key

        with open(self._key_path, "rb") as f:
            private_key = load_pem_private_key(f.read(), password=None)
        now = int(time.time())
        return jwt.encode(
            {"iss": self._team_id, "iat": now},
            private_key,
            algorithm="ES256",
            headers={"kid": self._key_id},
        )

    def send(self, tokens: Iterable[str], payload: PushPayload) -> None:
        import httpx
        import json

        body = {
            "aps": {
                "alert": {"title": payload.title, "body": payload.body},
                "sound": "default",
            }
        }
        if payload.badge is not None:
            body["aps"]["badge"] = payload.badge
        if payload.data:
            body.update(payload.data)

        token_jwt = self._jwt()
        headers = {
            "authorization": f"bearer {token_jwt}",
            "apns-topic": self._topic,
            "apns-push-type": "alert",
            "content-type": "application/json",
        }
        body_json = json.dumps(body)

        with httpx.Client(http2=True, timeout=10.0) as client:
            for device_token in tokens:
                try:
                    http_breaker.call(
                        client.post,
                        f"{self._host}/3/device/{device_token}",
                        headers=headers,
                        content=body_json,
                    )
                except Exception as e:
                    logger.warning("APNs send failed for token %s...: %s", device_token[:8], e)


def get_push_sender() -> PushSenderPort:
    key_path = os.getenv("APNS_KEY_PATH")
    key_id = os.getenv("APNS_KEY_ID")
    team_id = os.getenv("APNS_TEAM_ID")
    topic = os.getenv("APNS_TOPIC")
    if not (key_path and key_id and team_id and topic):
        return NoopPushSender()
    return APNsPushSender(
        key_path=key_path,
        key_id=key_id,
        team_id=team_id,
        topic=topic,
        sandbox=os.getenv("APNS_SANDBOX", "false").lower() == "true",
    )
