"""Regression tests for the video editor + export pipeline.

The editor router previously 500'd on every request (a local get_current_user
returned a dict while endpoints used attribute access) and the project repo
mis-mapped extra_metadata -> metadata. These tests lock in the fixes and the
real export wiring.
"""
import uuid


def _auth(client):
    email = f"ed_{uuid.uuid4().hex[:8]}@t.co"
    client.post("/auth/register", json={
        "email": email, "password": "Passw0rd!23",
        "username": email.split("@")[0], "date_of_birth": "2000-01-01",
        "accepted_terms": True,
    })
    tok = client.post("/auth/login", json={
        "email": email, "password": "Passw0rd!23",
    }).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def _create_project(client, headers):
    r = client.post("/api/editor/projects", data={"title": "T"}, headers=headers)
    assert r.status_code == 200, r.text
    return r.json()["project"]["id"]


def test_create_and_get_project(client):
    h = _auth(client)
    pid = _create_project(client, h)
    r = client.get(f"/api/editor/projects/{pid}", headers=h)
    assert r.status_code == 200
    assert r.json()["project"]["id"] == pid


def test_list_projects(client):
    h = _auth(client)
    _create_project(client, h)
    r = client.get("/api/editor/projects", headers=h)
    assert r.status_code == 200
    assert len(r.json()["projects"]) >= 1


def test_export_status_starts_not_started(client):
    h = _auth(client)
    pid = _create_project(client, h)
    r = client.get(f"/api/editor/projects/{pid}/export-status", headers=h)
    assert r.status_code == 200
    assert r.json()["export_status"] == "not_started"


def test_export_rejects_bad_quality(client):
    h = _auth(client)
    pid = _create_project(client, h)
    r = client.post(f"/api/editor/projects/{pid}/export",
                    json={"quality": "9000p"}, headers=h)
    assert r.status_code == 400


def test_export_marks_processing(client):
    h = _auth(client)
    pid = _create_project(client, h)
    r = client.post(f"/api/editor/projects/{pid}/export",
                    json={"quality": "1080p"}, headers=h)
    assert r.status_code == 200
    assert r.json()["export_settings"]["status"] == "processing"


def test_export_task_no_clips_marks_failed(client):
    """The render task fails cleanly (not a crash) when there is nothing to render."""
    from backend.infrastructure.queue.tasks import export_project_task
    from backend.infrastructure.repositories.database import get_task_session
    from backend.infrastructure.repositories.models import VideoProjectDB
    import json

    with get_task_session() as s:
        p = VideoProjectDB(user_id="u1", title="T")
        s.add(p); s.commit(); s.refresh(p)
        pid = p.id
    export_project_task(pid, "1080p")
    with get_task_session() as s:
        p = s.get(VideoProjectDB, pid)
        meta = json.loads(p.extra_metadata)
    assert meta["export"]["status"] == "failed"
    assert "clip" in meta["export"]["error"].lower()
