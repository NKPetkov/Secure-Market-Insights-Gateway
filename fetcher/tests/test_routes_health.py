"""Unit tests for health route."""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Test cases for health check endpoint."""

    def test_health_check_returns_200(self, client):
        """Test health endpoint returns 200 OK."""
        response = client.get("/v1/health")
        assert response.status_code == 200

    def test_health_check_returns_correct_structure(self, client):
        """Test health endpoint returns correct JSON structure."""
        response = client.get("/v1/health")
        data = response.json()

        assert "status" in data
        assert "timestamp" in data

    def test_health_check_status_is_healthy(self, client):
        """Test health endpoint returns healthy status."""
        response = client.get("/v1/health")
        data = response.json()

        assert data["status"] == "healthy"

    def test_health_check_timestamp_is_valid(self, client):
        """Test health endpoint returns valid timestamp."""
        response = client.get("/v1/health")
        data = response.json()

        # Verify timestamp can be parsed as datetime
        timestamp_str = data["timestamp"]
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        assert isinstance(timestamp, datetime)

    def test_health_check_no_authentication_required(self, client):
        """Test health endpoint doesn't require authentication."""
        # No authorization header provided
        response = client.get("/v1/health")
        assert response.status_code == 200

    def test_health_check_multiple_calls(self, client):
        """Test health endpoint can be called multiple times."""
        for _ in range(5):
            response = client.get("/v1/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"

    def test_health_check_content_type(self, client):
        """Test health endpoint returns JSON content type."""
        response = client.get("/v1/health")
        assert "application/json" in response.headers["content-type"]
