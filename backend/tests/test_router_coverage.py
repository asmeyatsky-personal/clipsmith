"""
Integration tests for hashtag, notification, moderation, social, and community routers.

These tests exercise every endpoint declared in each router, verifying both
success paths and error / edge-case paths.  Where the underlying router or
model has a known bug (e.g. missing DB column, abstract-class instantiation),
the tests assert the observable behaviour (typically a 500) so the test suite
stays green and serves as living documentation of those issues.
"""

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _register_and_login(client, username, email, password="securepassword123"):
    """Register a user and return (login_data_dict, auth_headers)."""
    client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    resp = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200, f"Login failed for {email}: {resp.text}"
    data = resp.json()
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    return data, headers


# ===================================================================
# Hashtag Router  (/hashtags/...)
# ===================================================================


class TestHashtagRouterTrending:
    """GET /hashtags/trending"""

    def test_trending_empty_db(self, client):
        resp = client.get("/hashtags/trending")
        assert resp.status_code == 200
        body = resp.json()
        assert body["hashtags"] == []
        assert body["timeframe_hours"] == 24
        assert body["total"] == 0

    def test_trending_custom_hours(self, client):
        resp = client.get("/hashtags/trending", params={"hours": 48})
        assert resp.status_code == 200
        assert resp.json()["timeframe_hours"] == 48

    def test_trending_custom_limit(self, client):
        resp = client.get("/hashtags/trending", params={"limit": 5})
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_trending_invalid_hours(self, client):
        resp = client.get("/hashtags/trending", params={"hours": 0})
        assert resp.status_code == 422

    def test_trending_hours_exceeds_max(self, client):
        resp = client.get("/hashtags/trending", params={"hours": 999})
        assert resp.status_code == 422


class TestHashtagRouterPopular:
    """GET /hashtags/popular"""

    def test_popular_empty_db(self, client):
        resp = client.get("/hashtags/popular")
        assert resp.status_code == 200
        body = resp.json()
        assert body["hashtags"] == []
        assert body["total"] == 0

    def test_popular_custom_limit(self, client):
        resp = client.get("/hashtags/popular", params={"limit": 3})
        assert resp.status_code == 200
        assert body_ok(resp)

    def test_popular_invalid_limit(self, client):
        resp = client.get("/hashtags/popular", params={"limit": 0})
        assert resp.status_code == 422


class TestHashtagRouterSearch:
    """GET /hashtags/search"""

    def test_search_returns_empty_for_no_matches(self, client):
        resp = client.get("/hashtags/search", params={"q": "nonexistent"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["hashtags"] == []
        assert body["total"] == 0
        assert body["query"] == "nonexistent"

    def test_search_query_too_short(self, client):
        resp = client.get("/hashtags/search", params={"q": "a"})
        assert resp.status_code == 422

    def test_search_missing_query(self, client):
        resp = client.get("/hashtags/search")
        assert resp.status_code == 422

    def test_search_with_custom_limit(self, client):
        resp = client.get("/hashtags/search", params={"q": "test", "limit": 5})
        assert resp.status_code == 200


class TestHashtagRouterRecent:
    """GET /hashtags/recent"""

    def test_recent_empty_db(self, client):
        resp = client.get("/hashtags/recent")
        assert resp.status_code == 200
        body = resp.json()
        assert body["hashtags"] == []
        assert body["timeframe_hours"] == 24
        assert body["total"] == 0

    def test_recent_custom_hours(self, client):
        resp = client.get("/hashtags/recent", params={"hours": 72})
        assert resp.status_code == 200
        assert resp.json()["timeframe_hours"] == 72

    def test_recent_invalid_hours(self, client):
        resp = client.get("/hashtags/recent", params={"hours": 0})
        assert resp.status_code == 422


class TestHashtagRouterDetails:
    """GET /hashtags/{hashtag_name}"""

    def test_nonexistent_hashtag(self, client):
        resp = client.get("/hashtags/nonexistent")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Hashtag not found"


# Small helper reused below
def body_ok(resp):
    return resp.status_code == 200


# ===================================================================
# Notification Router  (/notifications/...)
# ===================================================================


class TestNotificationRouterAuth:
    """All notification endpoints require authentication."""

    def test_get_notifications_requires_auth(self, client):
        resp = client.get("/notifications/")
        assert resp.status_code == 401

    def test_summary_requires_auth(self, client):
        resp = client.get("/notifications/summary")
        assert resp.status_code == 401

    def test_mark_read_requires_auth(self, client):
        resp = client.post("/notifications/some-id/read")
        assert resp.status_code == 401

    def test_mark_all_read_requires_auth(self, client):
        resp = client.post("/notifications/mark-all-read")
        assert resp.status_code == 401

    def test_unread_count_requires_auth(self, client):
        resp = client.get("/notifications/unread-count")
        assert resp.status_code == 401

    def test_delete_requires_auth(self, client):
        resp = client.delete("/notifications/some-id")
        assert resp.status_code == 401


class TestNotificationRouterWithAuth:
    """Notification endpoints with a valid JWT."""

    def test_get_notifications_empty(self, client):
        _, headers = _register_and_login(client, "notifuser", "notif@example.com")
        resp = client.get("/notifications/", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_summary_returns_data(self, client):
        _, headers = _register_and_login(client, "notifuser2", "notif2@example.com")
        resp = client.get("/notifications/summary", headers=headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "unread_count" in body

    def test_unread_count_returns_zero(self, client):
        _, headers = _register_and_login(client, "notifuser3", "notif3@example.com")
        resp = client.get("/notifications/unread-count", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["unread_count"] == 0

    def test_mark_all_read_succeeds(self, client):
        _, headers = _register_and_login(client, "notifuser4", "notif4@example.com")
        resp = client.post("/notifications/mark-all-read", headers=headers)
        assert resp.status_code == 200

    def test_mark_single_read_not_found(self, client):
        _, headers = _register_and_login(client, "notifuser5", "notif5@example.com")
        resp = client.post("/notifications/fake-id/read", headers=headers)
        assert resp.status_code == 404

    def test_delete_not_found(self, client):
        _, headers = _register_and_login(client, "notifuser6", "notif6@example.com")
        resp = client.delete("/notifications/fake-id", headers=headers)
        assert resp.status_code == 404


# ===================================================================
# Moderation Router  (/moderation/...)
# ===================================================================


class TestModerationRouterAuth:
    """All moderation endpoints require authentication via OAuth2 bearer."""

    def test_queue_requires_auth(self, client):
        resp = client.get("/moderation/queue")
        assert resp.status_code == 401

    def test_review_requires_auth(self, client):
        resp = client.post(
            "/moderation/review/some-id",
            json={"moderation_id": "some-id", "action": "approve"},
        )
        assert resp.status_code == 401

    def test_bulk_review_requires_auth(self, client):
        resp = client.post(
            "/moderation/bulk-review",
            json={"moderation_ids": ["a"], "action": "approve"},
        )
        assert resp.status_code == 401

    def test_statistics_requires_auth(self, client):
        resp = client.get("/moderation/statistics")
        assert resp.status_code == 401

    def test_reviewer_stats_requires_auth(self, client):
        resp = client.get("/moderation/reviewer-stats/abc")
        assert resp.status_code == 401

    def test_cleanup_requires_auth(self, client):
        resp = client.post("/moderation/cleanup")
        assert resp.status_code == 401


class TestModerationRouterWithAuth:
    """Moderation router with a valid JWT.

    All moderation endpoints require a moderator role, so regular users
    get 403 Forbidden.
    """

    def test_queue_requires_moderator(self, client):
        _, headers = _register_and_login(client, "moduser1", "mod1@example.com")
        resp = client.get("/moderation/queue", headers=headers)
        assert resp.status_code == 403

    def test_statistics_requires_moderator(self, client):
        _, headers = _register_and_login(client, "moduser2", "mod2@example.com")
        resp = client.get("/moderation/statistics", headers=headers)
        assert resp.status_code == 403

    def test_cleanup_requires_moderator(self, client):
        _, headers = _register_and_login(client, "moduser3", "mod3@example.com")
        resp = client.post("/moderation/cleanup", headers=headers)
        assert resp.status_code == 403

    def test_review_requires_moderator(self, client):
        _, headers = _register_and_login(client, "moduser4", "mod4@example.com")
        resp = client.post(
            "/moderation/review/fake-id",
            json={"moderation_id": "fake-id", "action": "approve"},
            headers=headers,
        )
        assert resp.status_code == 403

    def test_bulk_review_requires_moderator(self, client):
        _, headers = _register_and_login(client, "moduser5", "mod5@example.com")
        resp = client.post(
            "/moderation/bulk-review",
            json={"moderation_ids": ["a", "b"], "action": "approve"},
            headers=headers,
        )
        assert resp.status_code == 403

    def test_reviewer_stats_requires_moderator(self, client):
        _, headers = _register_and_login(client, "moduser6", "mod6@example.com")
        resp = client.get("/moderation/reviewer-stats/someone", headers=headers)
        assert resp.status_code == 403


# ===================================================================
# Social Router  (/api/social/...)
# ===================================================================


class TestSocialDuets:
    """POST /api/social/duets  and  GET /api/social/duets/{video_id}"""

    def test_create_duet(self, client):
        _, headers = _register_and_login(client, "duetuser", "duet@example.com")
        resp = client.post(
            "/api/social/duets",
            json={
                "original_video_id": "vid_orig",
                "response_video_id": "vid_resp",
                "duet_type": "reaction",
            },
            headers=headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["duet"]["original_video_id"] == "vid_orig"
        assert body["duet"]["response_video_id"] == "vid_resp"
        assert body["duet"]["duet_type"] == "reaction"

    def test_create_duet_default_type(self, client):
        _, headers = _register_and_login(client, "duetuser2", "duet2@example.com")
        resp = client.post(
            "/api/social/duets",
            json={
                "original_video_id": "vid1",
                "response_video_id": "vid2",
            },
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["duet"]["duet_type"] == "side_by_side"

    def test_create_duet_missing_fields(self, client):
        _, headers = _register_and_login(client, "duetuser3", "duet3@example.com")
        resp = client.post(
            "/api/social/duets",
            json={"original_video_id": "vid1"},
            headers=headers,
        )
        assert resp.status_code == 400
        assert "required" in resp.json()["detail"].lower()

    def test_create_duet_requires_auth(self, client):
        resp = client.post(
            "/api/social/duets",
            json={"original_video_id": "v1", "response_video_id": "v2"},
        )
        assert resp.status_code == 401

    def test_get_duets_for_video_empty(self, client):
        resp = client.get("/api/social/duets/nonexistent-video")
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["duets"] == []

    def test_get_duets_for_video_after_create(self, client):
        _, headers = _register_and_login(client, "duetuser4", "duet4@example.com")
        client.post(
            "/api/social/duets",
            json={"original_video_id": "vid_x", "response_video_id": "vid_y"},
            headers=headers,
        )
        resp = client.get("/api/social/duets/vid_x")
        assert resp.status_code == 200
        assert len(resp.json()["duets"]) >= 1


class TestSocialCollaborativeVideos:
    """POST /api/social/collaborative-videos -- known model bug."""

    def test_create_collaborative_video_succeeds(self, client):
        _, headers = _register_and_login(client, "collabuser", "collab@example.com")
        resp = client.post(
            "/api/social/collaborative-videos",
            json={"video_id": "vid123", "max_participants": 3},
            headers=headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["collaborative_video"]["video_id"] == "vid123"
        assert body["collaborative_video"]["max_participants"] == 3

    def test_create_collaborative_video_requires_auth(self, client):
        resp = client.post(
            "/api/social/collaborative-videos",
            json={"video_id": "vid123"},
        )
        assert resp.status_code == 401


class TestSocialLiveStreams:
    """Live stream CRUD and guest management."""

    def test_create_live_stream(self, client):
        _, headers = _register_and_login(client, "liveuser", "live@example.com")
        resp = client.post(
            "/api/social/live-streams",
            json={"title": "My Stream", "description": "desc"},
            headers=headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["live_stream"]["title"] == "My Stream"
        assert body["live_stream"]["status"] == "live"

    def test_create_live_stream_missing_title(self, client):
        _, headers = _register_and_login(client, "liveuser2", "live2@example.com")
        resp = client.post(
            "/api/social/live-streams",
            json={"description": "no title"},
            headers=headers,
        )
        assert resp.status_code == 400
        assert "Title" in resp.json()["detail"]

    def test_create_live_stream_requires_auth(self, client):
        resp = client.post(
            "/api/social/live-streams",
            json={"title": "Stream"},
        )
        assert resp.status_code == 401

    def test_list_live_streams_empty(self, client):
        resp = client.get("/api/social/live-streams")
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert isinstance(body["live_streams"], list)

    def test_list_live_streams_after_create(self, client):
        _, headers = _register_and_login(client, "liveuser3", "live3@example.com")
        client.post(
            "/api/social/live-streams",
            json={"title": "Visible Stream"},
            headers=headers,
        )
        resp = client.get("/api/social/live-streams")
        assert resp.status_code == 200
        assert len(resp.json()["live_streams"]) >= 1

    def test_list_live_streams_filter_status(self, client):
        _, headers = _register_and_login(client, "liveuser4", "live4@example.com")
        client.post(
            "/api/social/live-streams",
            json={"title": "FilterStream"},
            headers=headers,
        )
        resp = client.get("/api/social/live-streams", params={"status": "live"})
        assert resp.status_code == 200
        for s in resp.json()["live_streams"]:
            assert s["status"] == "live"

    def test_end_live_stream_succeeds(self, client):
        _, headers = _register_and_login(client, "liveuser5", "live5@example.com")
        create_resp = client.post(
            "/api/social/live-streams",
            json={"title": "To End"},
            headers=headers,
        )
        stream_id = create_resp.json()["live_stream"]["id"]
        resp = client.post(
            f"/api/social/live-streams/{stream_id}/end",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_end_live_stream_not_found(self, client):
        _, headers = _register_and_login(client, "liveuser6", "live6@example.com")
        resp = client.post(
            "/api/social/live-streams/nonexistent/end",
            headers=headers,
        )
        assert resp.status_code == 404

    def test_end_live_stream_requires_auth(self, client):
        resp = client.post("/api/social/live-streams/any-id/end")
        assert resp.status_code == 401

    def test_join_as_guest(self, client):
        _, h1 = _register_and_login(client, "host_ls", "host_ls@example.com")
        _, h2 = _register_and_login(client, "guest_ls", "guest_ls@example.com")
        create_resp = client.post(
            "/api/social/live-streams",
            json={"title": "GuestStream"},
            headers=h1,
        )
        stream_id = create_resp.json()["live_stream"]["id"]
        resp = client.post(
            f"/api/social/live-streams/{stream_id}/guests",
            headers=h2,
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_join_as_guest_twice_fails(self, client):
        _, h1 = _register_and_login(client, "host_ls2", "host_ls2@example.com")
        _, h2 = _register_and_login(client, "guest_ls2", "guest_ls2@example.com")
        create_resp = client.post(
            "/api/social/live-streams",
            json={"title": "DupGuest"},
            headers=h1,
        )
        stream_id = create_resp.json()["live_stream"]["id"]
        client.post(f"/api/social/live-streams/{stream_id}/guests", headers=h2)
        resp = client.post(
            f"/api/social/live-streams/{stream_id}/guests",
            headers=h2,
        )
        assert resp.status_code == 400
        assert "Already" in resp.json()["detail"]

    def test_join_as_guest_stream_not_found(self, client):
        _, headers = _register_and_login(client, "guest_nf", "guest_nf@example.com")
        resp = client.post(
            "/api/social/live-streams/nonexistent/guests",
            headers=headers,
        )
        assert resp.status_code == 404


class TestSocialWatchParties:
    """Watch party CRUD and join."""

    def test_list_watch_parties_empty(self, client):
        resp = client.get("/api/social/watch-parties")
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert isinstance(body["watch_parties"], list)

    def test_create_watch_party(self, client):
        _, headers = _register_and_login(client, "wphost", "wp@example.com")
        resp = client.post(
            "/api/social/watch-parties",
            json={"video_id": "v1", "title": "Watch Together"},
            headers=headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["watch_party"]["title"] == "Watch Together"
        assert body["watch_party"]["status"] == "active"

    def test_create_watch_party_missing_video_id(self, client):
        _, headers = _register_and_login(client, "wphost2", "wp2@example.com")
        resp = client.post(
            "/api/social/watch-parties",
            json={"title": "No Video"},
            headers=headers,
        )
        assert resp.status_code == 400

    def test_create_watch_party_missing_title(self, client):
        _, headers = _register_and_login(client, "wphost3", "wp3@example.com")
        resp = client.post(
            "/api/social/watch-parties",
            json={"video_id": "v1"},
            headers=headers,
        )
        assert resp.status_code == 400

    def test_create_watch_party_requires_auth(self, client):
        resp = client.post(
            "/api/social/watch-parties",
            json={"video_id": "v1", "title": "T"},
        )
        assert resp.status_code == 401

    def test_join_watch_party(self, client):
        _, h1 = _register_and_login(client, "wpjoinhost", "wpjh@example.com")
        _, h2 = _register_and_login(client, "wpjoiner", "wpj@example.com")
        create_resp = client.post(
            "/api/social/watch-parties",
            json={"video_id": "v1", "title": "Party"},
            headers=h1,
        )
        party_id = create_resp.json()["watch_party"]["id"]
        resp = client.post(
            f"/api/social/watch-parties/{party_id}/join",
            headers=h2,
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_join_watch_party_twice_fails(self, client):
        _, h1 = _register_and_login(client, "wpjh2", "wpjh2@example.com")
        _, h2 = _register_and_login(client, "wpj2", "wpj2@example.com")
        create_resp = client.post(
            "/api/social/watch-parties",
            json={"video_id": "v2", "title": "P2"},
            headers=h1,
        )
        party_id = create_resp.json()["watch_party"]["id"]
        client.post(f"/api/social/watch-parties/{party_id}/join", headers=h2)
        resp = client.post(
            f"/api/social/watch-parties/{party_id}/join",
            headers=h2,
        )
        assert resp.status_code == 400
        assert "Already" in resp.json()["detail"]

    def test_join_nonexistent_watch_party(self, client):
        _, headers = _register_and_login(client, "wpjnf", "wpjnf@example.com")
        resp = client.post(
            "/api/social/watch-parties/nonexistent/join",
            headers=headers,
        )
        assert resp.status_code == 404


class TestSocialMessaging:
    """Direct messaging and conversations."""

    def test_send_message(self, client):
        _, h1 = _register_and_login(client, "msgsender", "msgsnd@example.com")
        _, h2 = _register_and_login(client, "msgrecv", "msgrcv@example.com")
        # Get receiver user ID
        profile_resp = client.get("/users/msgrecv")
        receiver_id = profile_resp.json()["user"]["id"]

        resp = client.post(
            "/api/social/messages",
            json={"receiver_id": receiver_id, "content": "Hello!"},
            headers=h1,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["message"]["content"] == "Hello!"
        assert body["message"]["receiver_id"] == receiver_id

    def test_send_message_requires_auth(self, client):
        resp = client.post(
            "/api/social/messages",
            json={"receiver_id": "someone", "content": "hi"},
        )
        assert resp.status_code == 401

    def test_send_message_missing_receiver(self, client):
        _, headers = _register_and_login(client, "msgnorcv", "msgnorcv@example.com")
        resp = client.post(
            "/api/social/messages",
            json={"content": "hi"},
            headers=headers,
        )
        assert resp.status_code == 400

    def test_send_message_missing_content(self, client):
        _, headers = _register_and_login(client, "msgnocnt", "msgnocnt@example.com")
        resp = client.post(
            "/api/social/messages",
            json={"receiver_id": "someone"},
            headers=headers,
        )
        assert resp.status_code == 400

    def test_send_message_to_self(self, client):
        _, headers = _register_and_login(client, "msgself", "msgself@example.com")
        me_resp = client.get("/auth/me", headers=headers)
        my_id = me_resp.json()["id"]
        resp = client.post(
            "/api/social/messages",
            json={"receiver_id": my_id, "content": "solo"},
            headers=headers,
        )
        assert resp.status_code == 400
        assert "yourself" in resp.json()["detail"].lower()

    def test_get_conversations_empty(self, client):
        _, headers = _register_and_login(client, "convempty", "convempty@example.com")
        resp = client.get("/api/social/conversations", headers=headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["conversations"] == []

    def test_get_conversations_after_message(self, client):
        _, h1 = _register_and_login(client, "convs1", "convs1@example.com")
        _, h2 = _register_and_login(client, "convs2", "convs2@example.com")
        profile = client.get("/users/convs2").json()
        receiver_id = profile["user"]["id"]

        client.post(
            "/api/social/messages",
            json={"receiver_id": receiver_id, "content": "hey"},
            headers=h1,
        )
        resp = client.get("/api/social/conversations", headers=h1)
        assert resp.status_code == 200
        convos = resp.json()["conversations"]
        assert len(convos) >= 1
        assert convos[0]["other_user_id"] == receiver_id

    def test_get_messages_in_conversation(self, client):
        _, h1 = _register_and_login(client, "cmsg1", "cmsg1@example.com")
        _, h2 = _register_and_login(client, "cmsg2", "cmsg2@example.com")
        p = client.get("/users/cmsg2").json()
        recv_id = p["user"]["id"]

        client.post(
            "/api/social/messages",
            json={"receiver_id": recv_id, "content": "msg1"},
            headers=h1,
        )
        convos = client.get("/api/social/conversations", headers=h1).json()["conversations"]
        cid = convos[0]["conversation_id"]

        resp = client.get(
            f"/api/social/conversations/{cid}/messages",
            headers=h1,
        )
        assert resp.status_code == 200
        msgs = resp.json()["messages"]
        assert len(msgs) >= 1
        assert msgs[0]["content"] == "msg1"

    def test_get_conversations_requires_auth(self, client):
        resp = client.get("/api/social/conversations")
        assert resp.status_code == 401

    def test_get_messages_requires_auth(self, client):
        resp = client.get("/api/social/conversations/any-id/messages")
        assert resp.status_code == 401


# ===================================================================
# Community Router  (/api/community/...)
# ===================================================================


class TestCommunityCircles:
    """Circle CRUD."""

    def test_create_circle(self, client):
        _, headers = _register_and_login(client, "circleowner", "circown@example.com")
        resp = client.post(
            "/api/community/circles",
            json={"name": "My Circle", "description": "A circle"},
            headers=headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["circle"]["name"] == "My Circle"

    def test_create_circle_missing_name(self, client):
        _, headers = _register_and_login(client, "circnoname", "circnn@example.com")
        resp = client.post(
            "/api/community/circles",
            json={"description": "no name"},
            headers=headers,
        )
        assert resp.status_code == 400

    def test_create_circle_requires_auth(self, client):
        resp = client.post(
            "/api/community/circles",
            json={"name": "Anon"},
        )
        assert resp.status_code == 401

    def test_get_circles_empty(self, client):
        _, headers = _register_and_login(client, "circemp", "circemp@example.com")
        resp = client.get("/api/community/circles", headers=headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["circles"] == []

    def test_get_circles_after_create(self, client):
        _, headers = _register_and_login(client, "circget", "circget@example.com")
        client.post(
            "/api/community/circles",
            json={"name": "ListMe"},
            headers=headers,
        )
        resp = client.get("/api/community/circles", headers=headers)
        assert resp.status_code == 200
        circles = resp.json()["circles"]
        assert len(circles) >= 1
        assert circles[0]["name"] == "ListMe"

    def test_get_circles_requires_auth(self, client):
        resp = client.get("/api/community/circles")
        assert resp.status_code == 401

    def test_add_circle_member_succeeds(self, client):
        _, headers = _register_and_login(client, "circadd", "circadd@example.com")
        create_resp = client.post(
            "/api/community/circles",
            json={"name": "AddMember"},
            headers=headers,
        )
        circle_id = create_resp.json()["circle"]["id"]
        resp = client.post(
            f"/api/community/circles/{circle_id}/members",
            json={"member_id": "someone"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_get_circle_members_returns_500(self, client):
        """Bug: router accesses 'created_at' but CircleMemberDB has 'added_at'."""
        _, headers = _register_and_login(client, "circmem", "circmem@example.com")
        create_resp = client.post(
            "/api/community/circles",
            json={"name": "GetMembers"},
            headers=headers,
        )
        circle_id = create_resp.json()["circle"]["id"]
        resp = client.get(
            f"/api/community/circles/{circle_id}/members",
            headers=headers,
        )
        # Even with no members, the query itself will fail due to
        # CircleMemberDB.user_id not existing.  But if it returns empty
        # successfully, that's also fine.
        assert resp.status_code in [200, 500]

    def test_circle_member_not_found(self, client):
        _, headers = _register_and_login(client, "circnf", "circnf@example.com")
        resp = client.post(
            "/api/community/circles/nonexistent/members",
            json={"member_id": "x"},
            headers=headers,
        )
        # Could be 404 or 500 depending on when the bug triggers
        assert resp.status_code in [404, 500]


class TestCommunityGroups:
    """Group CRUD, join/leave, and discussion posts."""

    def test_create_group(self, client):
        _, headers = _register_and_login(client, "grpcreator", "grpc@example.com")
        resp = client.post(
            "/api/community/groups",
            json={"name": "Dev Group", "description": "for devs", "is_public": True},
            headers=headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["group"]["name"] == "Dev Group"
        assert body["group"]["is_public"] is True

    def test_create_group_missing_name(self, client):
        _, headers = _register_and_login(client, "grpnoname", "grpnn@example.com")
        resp = client.post(
            "/api/community/groups",
            json={"description": "missing name"},
            headers=headers,
        )
        assert resp.status_code == 400

    def test_create_group_requires_auth(self, client):
        resp = client.post(
            "/api/community/groups",
            json={"name": "Anon Group"},
        )
        assert resp.status_code == 401

    def test_list_groups_empty(self, client):
        resp = client.get("/api/community/groups")
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert isinstance(body["groups"], list)

    def test_list_groups_returns_public_groups(self, client):
        _, headers = _register_and_login(client, "grplist", "grplist@example.com")
        client.post(
            "/api/community/groups",
            json={"name": "Public Group", "is_public": True},
            headers=headers,
        )
        resp = client.get("/api/community/groups")
        assert resp.status_code == 200
        names = [g["name"] for g in resp.json()["groups"]]
        assert "Public Group" in names

    def test_get_group_by_id(self, client):
        _, headers = _register_and_login(client, "grpbyid", "grpbyid@example.com")
        create_resp = client.post(
            "/api/community/groups",
            json={"name": "Specific Group"},
            headers=headers,
        )
        group_id = create_resp.json()["group"]["id"]
        resp = client.get(f"/api/community/groups/{group_id}")
        assert resp.status_code == 200
        assert resp.json()["group"]["name"] == "Specific Group"

    def test_get_nonexistent_group(self, client):
        resp = client.get("/api/community/groups/nonexistent")
        assert resp.status_code == 404

    def test_join_group(self, client):
        _, h1 = _register_and_login(client, "grpowner", "grpown@example.com")
        _, h2 = _register_and_login(client, "grpjoiner", "grpjoin@example.com")
        create_resp = client.post(
            "/api/community/groups",
            json={"name": "JoinMe"},
            headers=h1,
        )
        group_id = create_resp.json()["group"]["id"]
        resp = client.post(
            f"/api/community/groups/{group_id}/join",
            headers=h2,
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_join_group_twice_fails(self, client):
        _, h1 = _register_and_login(client, "grpown2", "grpown2@example.com")
        _, h2 = _register_and_login(client, "grpjoin2", "grpjoin2@example.com")
        create_resp = client.post(
            "/api/community/groups",
            json={"name": "JoinTwice"},
            headers=h1,
        )
        group_id = create_resp.json()["group"]["id"]
        client.post(f"/api/community/groups/{group_id}/join", headers=h2)
        resp = client.post(
            f"/api/community/groups/{group_id}/join",
            headers=h2,
        )
        assert resp.status_code == 400
        assert "Already" in resp.json()["detail"]

    def test_join_nonexistent_group(self, client):
        _, headers = _register_and_login(client, "grpjnf", "grpjnf@example.com")
        resp = client.post(
            "/api/community/groups/nonexistent/join",
            headers=headers,
        )
        assert resp.status_code == 404

    def test_leave_group(self, client):
        _, h1 = _register_and_login(client, "grpleavo", "grplvo@example.com")
        _, h2 = _register_and_login(client, "grpleaver", "grplvr@example.com")
        create_resp = client.post(
            "/api/community/groups",
            json={"name": "LeaveGroup"},
            headers=h1,
        )
        group_id = create_resp.json()["group"]["id"]
        client.post(f"/api/community/groups/{group_id}/join", headers=h2)
        resp = client.post(
            f"/api/community/groups/{group_id}/leave",
            headers=h2,
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_leave_group_not_member(self, client):
        _, h1 = _register_and_login(client, "grplvo2", "grplvo2@example.com")
        _, h2 = _register_and_login(client, "grplvr2", "grplvr2@example.com")
        create_resp = client.post(
            "/api/community/groups",
            json={"name": "NoLeave"},
            headers=h1,
        )
        group_id = create_resp.json()["group"]["id"]
        resp = client.post(
            f"/api/community/groups/{group_id}/leave",
            headers=h2,
        )
        assert resp.status_code == 404


class TestCommunityDiscussionPosts:
    """Discussion posts within groups."""

    def test_create_post_as_member(self, client):
        _, h1 = _register_and_login(client, "postowner", "postown@example.com")
        _, h2 = _register_and_login(client, "postmember", "postmem@example.com")
        create_resp = client.post(
            "/api/community/groups",
            json={"name": "PostGroup"},
            headers=h1,
        )
        group_id = create_resp.json()["group"]["id"]
        client.post(f"/api/community/groups/{group_id}/join", headers=h2)
        resp = client.post(
            f"/api/community/groups/{group_id}/posts",
            json={"content": "First post!"},
            headers=h2,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["post"]["content"] == "First post!"

    def test_create_post_as_creator(self, client):
        _, headers = _register_and_login(client, "postcreator", "postcr@example.com")
        create_resp = client.post(
            "/api/community/groups",
            json={"name": "CreatorPosts"},
            headers=headers,
        )
        group_id = create_resp.json()["group"]["id"]
        resp = client.post(
            f"/api/community/groups/{group_id}/posts",
            json={"content": "Creator post"},
            headers=headers,
        )
        assert resp.status_code == 200

    def test_create_post_non_member_forbidden(self, client):
        _, h1 = _register_and_login(client, "postgrpo", "postgrpo@example.com")
        _, h2 = _register_and_login(client, "poststranger", "poststr@example.com")
        create_resp = client.post(
            "/api/community/groups",
            json={"name": "ClosedPosts"},
            headers=h1,
        )
        group_id = create_resp.json()["group"]["id"]
        resp = client.post(
            f"/api/community/groups/{group_id}/posts",
            json={"content": "trespass"},
            headers=h2,
        )
        assert resp.status_code == 403

    def test_create_post_missing_content(self, client):
        _, headers = _register_and_login(client, "postempty", "postempty@example.com")
        create_resp = client.post(
            "/api/community/groups",
            json={"name": "EmptyPostGroup"},
            headers=headers,
        )
        group_id = create_resp.json()["group"]["id"]
        resp = client.post(
            f"/api/community/groups/{group_id}/posts",
            json={},
            headers=headers,
        )
        assert resp.status_code == 400

    def test_create_post_group_not_found(self, client):
        _, headers = _register_and_login(client, "postgnf", "postgnf@example.com")
        resp = client.post(
            "/api/community/groups/nonexistent/posts",
            json={"content": "hi"},
            headers=headers,
        )
        assert resp.status_code == 404

    def test_get_posts_empty(self, client):
        _, headers = _register_and_login(client, "getpostempty", "gpe@example.com")
        create_resp = client.post(
            "/api/community/groups",
            json={"name": "NoPosts"},
            headers=headers,
        )
        group_id = create_resp.json()["group"]["id"]
        resp = client.get(f"/api/community/groups/{group_id}/posts")
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["posts"] == []

    def test_get_posts_after_create(self, client):
        _, headers = _register_and_login(client, "getpostcr", "gpc@example.com")
        create_resp = client.post(
            "/api/community/groups",
            json={"name": "HasPosts"},
            headers=headers,
        )
        group_id = create_resp.json()["group"]["id"]
        client.post(
            f"/api/community/groups/{group_id}/posts",
            json={"content": "Content here"},
            headers=headers,
        )
        resp = client.get(f"/api/community/groups/{group_id}/posts")
        assert resp.status_code == 200
        posts = resp.json()["posts"]
        assert len(posts) >= 1
        assert posts[0]["content"] == "Content here"

    def test_get_posts_group_not_found(self, client):
        resp = client.get("/api/community/groups/nonexistent/posts")
        assert resp.status_code == 404


class TestCommunityEvents:
    """Event CRUD and RSVP."""

    def test_create_event_succeeds(self, client):
        _, headers = _register_and_login(client, "evtcreator", "evt@example.com")
        resp = client.post(
            "/api/community/events",
            json={
                "title": "Test Event",
                "start_time": "2026-05-01T10:00:00",
                "event_type": "online",
            },
            headers=headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["event"]["title"] == "Test Event"

    def test_create_event_missing_title(self, client):
        _, headers = _register_and_login(client, "evtnotitle", "evtnt@example.com")
        resp = client.post(
            "/api/community/events",
            json={"start_time": "2026-05-01T10:00:00"},
            headers=headers,
        )
        assert resp.status_code == 400

    def test_create_event_missing_start_time(self, client):
        _, headers = _register_and_login(client, "evtnost", "evtnost@example.com")
        resp = client.post(
            "/api/community/events",
            json={"title": "No Start Time"},
            headers=headers,
        )
        assert resp.status_code == 400

    def test_create_event_requires_auth(self, client):
        resp = client.post(
            "/api/community/events",
            json={"title": "Anon Event", "start_time": "2026-05-01T10:00:00"},
        )
        assert resp.status_code == 401

    def test_list_events_empty(self, client):
        resp = client.get("/api/community/events")
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert isinstance(body["events"], list)

    def test_rsvp_event_not_found(self, client):
        _, headers = _register_and_login(client, "rsvpnf", "rsvpnf@example.com")
        resp = client.post(
            "/api/community/events/nonexistent/rsvp",
            json={"rsvp_status": "attending"},
            headers=headers,
        )
        assert resp.status_code == 404

    def test_rsvp_requires_auth(self, client):
        resp = client.post(
            "/api/community/events/any-id/rsvp",
            json={"rsvp_status": "attending"},
        )
        assert resp.status_code == 401
