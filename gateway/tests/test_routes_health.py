"""Tests for health check endpoint."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for GET /v1/health endpoint."""

    def test_health_check_returns_200(self, client):
        """Test that health check returns 200 status code."""
        response = client.get("/v1/health")
        assert response.status_code == 200

    def test_health_check_response_structure(self, client):
        """Test health check response has correct structure."""
        response = client.get("/v1/health")
        data = response.json()

        assert "status" in data
        assert "timestamp" in data
        assert data["status"] in ["healthy", "degraded"]

    def test_health_check_no_auth_required(self, client):
        """Test that health check doesn't require authentication."""
        # Should work without any headers
        response = client.get("/v1/health")
        assert response.status_code == 200

    def test_health_check_with_degraded_redis(self, client, monkeypatch):
        """Test health check reports degraded when Redis is unavailable."""
        # Mock Redis health check to return False
        from app.dependencies import cache

        def mock_health_check_failed():
            return False

        monkeypatch.setattr(cache.cache, "health_check", mock_health_check_failed)

        response = client.get("/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"

    def test_health_check_with_healthy_redis(self, client, monkeypatch):
        """Test health check reports healthy when Redis is available."""
        from app.dependencies import cache

        def mock_health_check_success():
            return True

        monkeypatch.setattr(cache.cache, "health_check", mock_health_check_success)

        response = client.get("/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
