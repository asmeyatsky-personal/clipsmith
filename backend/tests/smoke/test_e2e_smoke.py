"""End-to-end smoke test — exercises real upload/feed/social/GDPR paths.

Runs against an in-memory SQLite by default; override DATABASE_URL to point
at a Neon test branch in CI.
"""
import os
import uuid
from datetime import date
from pathlib import Path

import pytest

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET_KEY", "smoke-test-secret-not-for-prod")
os.environ.setdefault("STORAGE_TYPE", "local")
os.environ.setdefault("UPLOAD_DIR", "/tmp/clipsmith-uploads")
os.environ.setdefault("STORAGE_BASE_URL", "http://localhost:8000/uploads")
Path(os.environ["UPLOAD_DIR"]).mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient
    from backend.main import app
    return TestClient(app)


@pytest.fixture(scope="module")
def tiny_video_path(tmp_path_factory):
    p = tmp_path_factory.mktemp("smoke") / "tiny.mp4"
    header = bytes.fromhex(
        "00000020"
        "66747970"
        "69736f6d"
        "0000020069736f6d69736f32617663316d703431"
    )
    p.write_bytes(header + b"\x00" * (50 * 1024 - len(header)))
    return p


@pytest.fixture(scope="module")
def users(client):
    sfx = uuid.uuid4().hex[:6]
    creds = {
        "alice": {
            "username": f"smoke_alice_{sfx}",
            "email": f"alice_{sfx}@example.com",
            "password": "S3cret-smoke-pw",
        },
        "bob": {
            "username": f"smoke_bob_{sfx}",
            "email": f"bob_{sfx}@example.com",
            "password": "S3cret-smoke-pw",
        },
    }
    tokens = {}
    ids = {}
    for name, c in creds.items():
        r = client.post("/auth/register", json={**c, "date_of_birth": "2000-01-01"})
        assert r.status_code == 201, r.text
        r = client.post("/auth/login", json={"email": c["email"], "password": c["password"]})
        assert r.status_code == 200, r.text
        tokens[name] = r.json()["access_token"]
        r = client.get("/auth/me", headers={"Authorization": f"Bearer {tokens[name]}"})
        assert r.status_code == 200
        ids[name] = r.json()["id"]
    return {"creds": creds, "tokens": tokens, "ids": ids}


def hdr(token):
    return {"Authorization": f"Bearer {token}"}


def test_age_gate_rejects_under_13(client):
    r = client.post(
        "/auth/register",
        json={
            "username": f"kid_{uuid.uuid4().hex[:6]}",
            "email": f"kid_{uuid.uuid4().hex[:6]}@example.com",
            "password": "S3cret-smoke-pw",
            "date_of_birth": (
                date.today().replace(year=date.today().year - 10)
            ).isoformat(),
        },
    )
    assert r.status_code == 422, r.text


def test_upload_video(client, users, tiny_video_path):
    with open(tiny_video_path, "rb") as f:
        r = client.post(
            "/videos/",
            headers=hdr(users["tokens"]["alice"]),
            data={"title": "Smoke clip", "description": "hello #smoke"},
            files={"file": ("smoke.mp4", f, "video/mp4")},
        )
    assert r.status_code == 200, r.text
    assert "id" in r.json()


def test_auto_reject_blatant_text(client, users, tiny_video_path):
    with open(tiny_video_path, "rb") as f:
        r = client.post(
            "/videos/",
            headers=hdr(users["tokens"]["alice"]),
            data={"title": "kill yourself", "description": "kill yourself"},
            files={"file": ("evil.mp4", f, "video/mp4")},
        )
    assert r.status_code == 200, r.text
    assert r.json().get("status") == "REJECTED"


def test_feed_endpoints(client, users):
    r = client.get("/feed/?feed_type=foryou", headers=hdr(users["tokens"]["alice"]))
    assert r.status_code == 200, r.text
    r = client.get("/feed/trending")
    assert r.status_code == 200, r.text


def test_interactions(client, users, tiny_video_path):
    with open(tiny_video_path, "rb") as f:
        r = client.post(
            "/videos/",
            headers=hdr(users["tokens"]["alice"]),
            data={"title": "Interaction target", "description": "smoke"},
            files={"file": ("inter.mp4", f, "video/mp4")},
        )
    if r.status_code == 429:
        pytest.skip("upload rate-limited")
    assert r.status_code == 200, r.text
    video_id = r.json()["id"]
    r = client.post(f"/videos/{video_id}/like", headers=hdr(users["tokens"]["bob"]))
    assert r.status_code == 200
    r = client.post(
        f"/videos/{video_id}/comments",
        headers=hdr(users["tokens"]["bob"]),
        json={"content": "great!"},
    )
    assert r.status_code in (200, 201)
    r = client.post(
        f"/videos/{video_id}/report",
        headers=hdr(users["tokens"]["bob"]),
        json={"reason": "spam"},
    )
    assert r.status_code in (200, 201)


def test_social_graph(client, users):
    bob_id = users["ids"]["bob"]
    r = client.post(f"/users/{bob_id}/follow", headers=hdr(users["tokens"]["alice"]))
    assert r.status_code == 201
    r = client.post(f"/users/{bob_id}/block", headers=hdr(users["tokens"]["alice"]))
    assert r.status_code == 201
    r = client.delete(f"/users/{bob_id}/block", headers=hdr(users["tokens"]["alice"]))
    assert r.status_code == 204


def test_profile_edit(client, users):
    r = client.patch(
        "/users/me",
        headers=hdr(users["tokens"]["alice"]),
        json={"bio": "Smoke test bio"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["bio"] == "Smoke test bio"


def test_followers_list(client, users):
    r = client.get(f"/users/{users['ids']['bob']}/followers")
    assert r.status_code == 200
    assert "items" in r.json()


def test_my_likes(client, users):
    r = client.get("/users/me/likes", headers=hdr(users["tokens"]["alice"]))
    assert r.status_code == 200
    assert "items" in r.json()


def test_gdpr_partial_delete(client, users):
    r = client.post(
        "/api/compliance/gdpr/delete",
        headers=hdr(users["tokens"]["bob"]),
        json={"categories": ["videos", "comments", "likes"]},
    )
    assert r.status_code == 200, r.text
