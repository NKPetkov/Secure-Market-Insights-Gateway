"""Unit tests for rate limiter module."""
import pytest
import time
from fastapi import HTTPException

from app.dependencies.rate_limiter import TokenRateLimiter


class TestTokenRateLimiter:
    """Tests for TokenRateLimiter class."""

    @pytest.fixture
    def rate_limiter(self):
        """Create a fresh rate limiter instance for each test."""
        return TokenRateLimiter()

    def test_allows_requests_within_limit(self, rate_limiter):
        """Test that requests within limit are allowed."""
        identifier = "test-token"

        # Should allow 10 requests (default limit)
        for i in range(10):
            rate_limiter.check_limit(identifier, rate_limit=10, time_limit=60)

        # All passed without exception

    def test_blocks_requests_exceeding_limit(self, rate_limiter):
        """Test that requests exceeding limit are blocked."""
        identifier = "test-token"

        # Fill up the limit
        for i in range(10):
            rate_limiter.check_limit(identifier, rate_limit=10, time_limit=60)

        # 11th request should be blocked
        with pytest.raises(HTTPException) as exc_info:
            rate_limiter.check_limit(identifier, rate_limit=10, time_limit=60)

        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in exc_info.value.detail

    def test_different_identifiers_have_separate_limits(self, rate_limiter):
        """Test that different identifiers have independent limits."""
        token1 = "token1"
        token2 = "token2"

        # Fill up limit for token1
        for i in range(10):
            rate_limiter.check_limit(token1, rate_limit=10, time_limit=60)

        # token2 should still have full limit available
        rate_limiter.check_limit(token2, rate_limit=10, time_limit=60)
        # Should not raise

    def test_old_requests_are_cleaned_up(self, rate_limiter):
        """Test that old requests outside window are cleaned up."""
        identifier = "test-token"

        # Add old requests (simulate by manipulating internal state)
        old_time = time.time() - 120  # 2 minutes ago
        rate_limiter._requests[identifier] = [old_time] * 10

        # New request should be allowed (old ones outside 60s window)
        rate_limiter.check_limit(identifier, rate_limit=10, time_limit=60)
        # Should not raise

    def test_sliding_window_behavior(self, rate_limiter):
        """Test that sliding window works correctly."""
        identifier = "test-token"
        current_time = time.time()

        # Add requests at different times within window
        rate_limiter._requests[identifier] = [
            current_time - 50,  # 50s ago
            current_time - 40,  # 40s ago
            current_time - 30,  # 30s ago
        ]

        # Should be able to add more requests (only 3 in window)
        for i in range(7):
            rate_limiter.check_limit(identifier, rate_limit=10, time_limit=60)

        # 11th should fail
        with pytest.raises(HTTPException):
            rate_limiter.check_limit(identifier, rate_limit=10, time_limit=60)

    def test_custom_rate_limit(self, rate_limiter):
        """Test custom rate limit parameter."""
        identifier = "test-token"

        # Use custom limit of 5
        for i in range(5):
            rate_limiter.check_limit(identifier, rate_limit=5, time_limit=60)

        # 6th should fail
        with pytest.raises(HTTPException) as exc_info:
            rate_limiter.check_limit(identifier, rate_limit=5, time_limit=60)

        assert "Maximum 5 requests" in exc_info.value.detail

    def test_custom_time_window(self, rate_limiter):
        """Test custom time window parameter."""
        identifier = "test-token"
        current_time = time.time()

        # Add request 35 seconds ago
        rate_limiter._requests[identifier] = [current_time - 35]

        # With 30s window, old request should be cleaned
        rate_limiter.check_limit(identifier, rate_limit=10, time_limit=30)

        # Should only have 1 request now (the new one)
        assert len(rate_limiter._requests[identifier]) == 1

    def test_retry_after_header_in_response(self, rate_limiter):
        """Test that 429 response includes Retry-After header."""
        identifier = "test-token"

        # Fill up limit
        for i in range(10):
            rate_limiter.check_limit(identifier, rate_limit=10, time_limit=60)

        # Exceed limit
        with pytest.raises(HTTPException) as exc_info:
            rate_limiter.check_limit(identifier, rate_limit=10, time_limit=60)

        assert "Retry-After" in exc_info.value.headers
        assert exc_info.value.headers["Retry-After"] == "60"

    def test_empty_identifier(self, rate_limiter):
        """Test behavior with empty identifier."""
        # Should work even with empty string
        rate_limiter.check_limit("", rate_limit=10, time_limit=60)

    def test_clean_old_requests_method(self, rate_limiter):
        """Test _clean_old_requests method directly."""
        identifier = "test-token"
        current_time = time.time()

        # Add mix of old and recent requests
        rate_limiter._requests[identifier] = [
            current_time - 120,  # Old (outside window)
            current_time - 90,   # Old
            current_time - 30,   # Recent (inside window)
            current_time - 10,   # Recent
        ]

        # Clean requests older than 60s
        window_start = current_time - 60
        rate_limiter._clean_old_requests(identifier, window_start)

        # Should only have 2 recent requests left
        assert len(rate_limiter._requests[identifier]) == 2
