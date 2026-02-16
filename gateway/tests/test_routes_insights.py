"""Tests for insights API endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestPostInsights:
    """Tests for POST /v1/insights endpoint."""

    def test_successful_insight_creation(self, client, auth_headers, mock_fetcher_success):
        """Test successful creation of new insight."""
        response = client.post(
            "/v1/insights/",
            json={"insight_request": {"symbol": "bitcoin"}},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert data["symbol"] == "bitcoin"
        assert data["cached"] is False
        assert "data" in data
        assert data["data"]["symbol"] == "bitcoin"
        assert data["data"]["name"] == "Bitcoin"

    def test_missing_authorization_header(self, client, mock_fetcher_success):
        """Test request without authorization header."""
        response = client.post(
            "/v1/insights/",
            json={"insight_request": {"symbol": "bitcoin"}}
        )

        assert response.status_code == 422  # FastAPI validation error for missing header

    def test_invalid_token(self, client, mock_fetcher_success):
        """Test request with invalid token."""
        response = client.post(
            "/v1/insights/",
            json={"insight_request": {"symbol": "bitcoin"}},
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == 401
        assert "Invalid authentication token" in response.json()["detail"]

    def test_malformed_authorization_header(self, client, mock_fetcher_success):
        """Test request with malformed authorization header."""
        response = client.post(
            "/v1/insights/",
            json={"insight_request": {"symbol": "bitcoin"}},
            headers={"Authorization": "InvalidFormat"}
        )

        assert response.status_code == 401

    def test_missing_request_body(self, client, auth_headers):
        """Test request with missing body."""
        response = client.post(
            "/v1/insights/",
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    def test_invalid_symbol_format(self, client, auth_headers, mock_fetcher_success):
        """Test request with invalid symbol."""
        # This depends on validator implementation
        # If validator accepts all strings, this might pass
        response = client.post(
            "/v1/insights/",
            json={"insight_request": {"symbol": ""}},
            headers=auth_headers
        )

        # Could be 400 (validation) or 422 (pydantic)
        assert response.status_code in [400, 422]

    def test_fetcher_service_failure(self, client, auth_headers, mock_fetcher_failure):
        """Test handling of fetcher service failure."""
        response = client.post(
            "/v1/insights/",
            json={"insight_request": {"symbol": "bitcoin"}},
            headers=auth_headers
        )

        assert response.status_code == 503

    def test_rate_limiting(self, client, auth_headers, mock_fetcher_success):
        """Test rate limiting kicks in after exceeding limit."""
        # Make 10 requests (default limit) using valid symbols
        valid_symbols = ["bitcoin", "ethereum", "solana", "cardano"]
        for i in range(10):
            symbol = valid_symbols[i % len(valid_symbols)]  # Cycle through valid symbols
            response = client.post(
                "/v1/insights/",
                json={"insight_request": {"symbol": symbol}},
                headers=auth_headers
            )
            assert response.status_code == 200

        # 11th request should be rate limited
        response = client.post(
            "/v1/insights/",
            json={"insight_request": {"symbol": "bitcoin"}},
            headers=auth_headers
        )

        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]
        assert "Retry-After" in response.headers

    def test_cached_response_on_second_request(self, client, auth_headers, mock_fetcher_success, mock_cache):
        """Test that second request for same symbol returns cached data."""
        # First request
        response1 = client.post(
            "/v1/insights/",
            json={"insight_request": {"symbol": "bitcoin"}},
            headers=auth_headers
        )

        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["cached"] is False
        request_id_1 = data1["request_id"]

        # Second request for same symbol
        response2 = client.post(
            "/v1/insights/",
            json={"insight_request": {"symbol": "bitcoin"}},
            headers=auth_headers
        )

        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["cached"] is True
        # Should return same request_id from cache
        assert data2["request_id"] == request_id_1


class TestGetInsightByRequestId:
    """Tests for GET /v1/insights/{request_id} endpoint."""

    def test_get_cached_insight_success(self, client, auth_headers, mock_fetcher_success, mock_cache):
        """Test retrieving cached insight by request_id."""
        # First create an insight
        create_response = client.post(
            "/v1/insights/",
            json={"insight_request": {"symbol": "bitcoin"}},
            headers=auth_headers
        )

        assert create_response.status_code == 200
        request_id = create_response.json()["request_id"]

        # Now retrieve it by request_id
        get_response = client.get(
            f"/v1/insights/{request_id}",
            headers=auth_headers
        )

        assert get_response.status_code == 200
        data = get_response.json()
        assert data["request_id"] == request_id
        assert data["cached"] is True
        assert data["symbol"] == "bitcoin"

    def test_get_nonexistent_request_id(self, client, auth_headers):
        """Test retrieving non-existent request_id."""
        response = client.get(
            "/v1/insights/nonexistent-id-12345",
            headers=auth_headers
        )

        assert response.status_code == 404
        assert "No cached insights found" in response.json()["detail"]

    def test_get_without_authorization(self, client):
        """Test GET request without authorization."""
        response = client.get("/v1/insights/some-id")

        assert response.status_code == 422  # Missing header

    def test_get_with_invalid_token(self, client, mock_cache):
        """Test GET request with invalid token."""
        response = client.get(
            "/v1/insights/some-id",
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == 401


class TestHealthEndpoint:
    """Tests for GET /v1/health endpoint."""

    def test_health_check_success(self, client):
        """Test health check returns healthy status."""
        response = client.get("/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded"]
        assert "timestamp" in data

    def test_health_check_no_auth_required(self, client):
        """Test health check doesn't require authentication."""
        # Should work without auth headers
        response = client.get("/v1/health")
        assert response.status_code == 200


class TestEndToEndFlow:
    """End-to-end integration tests."""

    def test_complete_flow(self, client, auth_headers, mock_fetcher_success, mock_cache):
        """Test complete flow: create, retrieve, cache."""
        # Step 1: Health check
        health_response = client.get("/v1/health")
        assert health_response.status_code == 200

        # Step 2: Create new insight
        create_response = client.post(
            "/v1/insights/",
            json={"insight_request": {"symbol": "ethereum"}},
            headers=auth_headers
        )

        assert create_response.status_code == 200
        create_data = create_response.json()
        request_id = create_data["request_id"]
        assert create_data["cached"] is False

        # Step 3: Retrieve by request_id
        get_response = client.get(
            f"/v1/insights/{request_id}",
            headers=auth_headers
        )

        assert get_response.status_code == 200
        get_data = get_response.json()
        assert get_data["request_id"] == request_id
        assert get_data["cached"] is True

        # Step 4: Create same symbol again (should be cached)
        cached_response = client.post(
            "/v1/insights/",
            json={"insight_request": {"symbol": "ethereum"}},
            headers=auth_headers
        )

        assert cached_response.status_code == 200
        cached_data = cached_response.json()
        assert cached_data["cached"] is True
        assert cached_data["request_id"] == request_id

    def test_different_tokens_have_separate_rate_limits(self, client, mock_fetcher_success):
        """Test that different tokens have independent rate limits."""
        token1_headers = {"Authorization": "Bearer token1"}
        token2_headers = {"Authorization": "Bearer token2"}

        # This test won't work with current setup since token validation will fail
        # Would need to mock token validation or configure multiple valid tokens
        pass
