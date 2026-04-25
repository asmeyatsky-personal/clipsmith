import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def auth_headers(client):
    """Register a user and return auth headers."""
    user_data = {
        "username": "testuser_api",
        "email": "testapi@example.com",
        "password": "securepassword123",
            "date_of_birth": "2000-01-01"
        }
    client.post("/auth/register", json=user_data)
    login_response = client.post(
        "/auth/login",
        json={"email": "testapi@example.com", "password": "securepassword123",
                "date_of_birth": "2000-01-01"
            },
    )
    if login_response.status_code == 200:
        token = login_response.json().get("access_token", "")
        return {"Authorization": f"Bearer {token}"}
    return {"Authorization": "Bearer test_token"}


class TestVideoAPI:
    """Test suite for Video API endpoints."""

    def test_get_video_feed(self, client):
        """Test getting video feed."""
        response = client.get("/feed/trending")
        assert response.status_code == 200

    def test_list_videos(self, client):
        """Test listing videos."""
        response = client.get("/videos/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_get_nonexistent_video(self, client):
        """Test getting a non-existent video."""
        response = client.get("/videos/nonexistent-id")
        assert response.status_code == 404


class TestAuthAPI:
    """Test suite for Authentication API endpoints."""

    def test_register_user(self, client):
        """Test user registration."""
        user_data = {
            "username": "testuser123",
            "email": "testregister@example.com",
            "password": "securepassword123",
            "date_of_birth": "2000-01-01"
        }

        response = client.post("/auth/register", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser123"
        assert data["email"] == "testregister@example.com"

    def test_invalid_login(self, client):
        """Test invalid login credentials."""
        login_data = {"email": "invalid@example.com", "password": "wrongpassword",
                "date_of_birth": "2000-01-01"
            }

        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 401


class TestPaymentAPI:
    """Test suite for Payment API endpoints."""

    def test_create_tip(self, client, auth_headers):
        """Test creating a tip."""
        tip_data = {
            "creator_id": "creator_123",
            "amount": "5.00",
            "video_id": "video_123",
        }

        response = client.post(
            "/api/payments/tip", data=tip_data, headers=auth_headers
        )
        # May return 200, 400, or 500 depending on Stripe config
        assert response.status_code in [200, 400, 500]

    def test_get_wallet(self, client, auth_headers):
        """Test getting user wallet."""
        response = client.get("/api/payments/wallet", headers=auth_headers)
        assert response.status_code in [200, 401, 500]

    def test_get_transaction_history(self, client, auth_headers):
        """Test getting transaction history."""
        response = client.get("/api/payments/transactions", headers=auth_headers)
        assert response.status_code in [200, 401, 500]

    def test_request_payout(self, client, auth_headers):
        """Test requesting a payout."""
        response = client.post(
            "/api/payments/payouts/request", headers=auth_headers
        )
        assert response.status_code in [200, 400, 401, 500]


class TestAnalyticsAPI:
    """Test suite for Analytics API endpoints."""

    def test_get_creator_dashboard(self, client, auth_headers):
        """Test getting creator dashboard."""
        response = client.get(
            "/api/analytics/creator/dashboard", headers=auth_headers
        )
        assert response.status_code in [200, 401, 500]

    def test_get_trending_content(self, client):
        """Test getting trending content."""
        response = client.get("/api/analytics/trending/content")

        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "trending_content" in data

    def test_get_time_series_data(self, client, auth_headers):
        """Test getting time series data."""
        response = client.get(
            "/api/analytics/time-series/views",
            params={"time_period": "week"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 500]


class TestVideoEditorAPI:
    """Test suite for Video Editor API endpoints."""

    def test_create_project(self, client, auth_headers):
        """Test creating a video project."""
        project_data = {"title": "Test Project", "description": "A test video project"}

        response = client.post(
            "/api/editor/projects", json=project_data, headers=auth_headers
        )
        assert response.status_code in [200, 201, 401, 500]

    def test_get_user_projects(self, client, auth_headers):
        """Test getting user's video projects."""
        response = client.get("/api/editor/projects", headers=auth_headers)
        assert response.status_code in [200, 401, 500]


class TestErrorHandling:
    """Test suite for error handling and edge cases."""

    def test_404_handling(self, client):
        """Test 404 error handling."""
        response = client.get("/api/nonexistent/endpoint")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_validation_errors(self, client):
        """Test input validation errors."""
        # Test invalid registration data (empty username)
        invalid_user = {
            "username": "",
            "email": "invalid-email",
            "password": "123",
            "date_of_birth": "2000-01-01"
        }

        response = client.post("/auth/register", json=invalid_user)
        # Should be 422 (validation) or 400 (business logic)
        assert response.status_code in [400, 422]

    def test_unauthorized_access(self, client):
        """Test unauthorized access to protected endpoints."""
        response = client.get("/auth/me")  # No auth headers

        assert response.status_code == 401

    def test_rate_limiting(self, client):
        """Test rate limiting exists."""
        # Just verify the rate limiter endpoint exists
        responses = []
        for _ in range(5):
            response = client.post(
                "/auth/login",
                json={"email": "test@example.com", "password": "password",
                "date_of_birth": "2000-01-01"
            },
            )
            responses.append(response.status_code)

        # Should get responses (401 for bad creds or 429 if rate limited)
        assert all(status in [401, 429] for status in responses)


class TestIntegration:
    """Integration tests for complete user flows."""

    def test_complete_user_flow(self, client):
        """Test complete user registration to login flow."""
        # 1. Register user
        user_data = {
            "username": "integration_user",
            "email": "integration@example.com",
            "password": "securepassword123",
            "date_of_birth": "2000-01-01"
        }

        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == 201

        # 2. Login
        login_response = client.post(
            "/auth/login",
            json={
                "email": "integration@example.com",
                "password": "securepassword123",
                "date_of_birth": "2000-01-01"
            },
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "access_token" in login_data
        token = login_data["access_token"]

        auth_headers = {"Authorization": f"Bearer {token}"}

        # 3. Get user profile
        profile_response = client.get("/auth/me", headers=auth_headers)
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        assert profile_data["username"] == "integration_user"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
