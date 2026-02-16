"""Unit tests for authentication module."""
import pytest
from fastapi import HTTPException

from app.dependencies.auth import validate_authorization_header, _check_header_exists, _validate_header_scheme
from app.config import settings


class TestCheckHeaderExists:
    """Tests for _check_header_exists function."""

    def test_missing_header_raises_401(self):
        """Test that missing header raises 401 error."""
        with pytest.raises(HTTPException) as exc_info:
            _check_header_exists(None)

        assert exc_info.value.status_code == 401
        assert "Missing Authorization header" in exc_info.value.detail

    def test_empty_string_header_raises_401(self):
        """Test that empty string header raises 401 error."""
        with pytest.raises(HTTPException) as exc_info:
            _check_header_exists("")

        assert exc_info.value.status_code == 401

    def test_valid_header_does_not_raise(self):
        """Test that valid header does not raise exception."""
        # Should not raise
        _check_header_exists("Bearer token123")


class TestValidateHeaderScheme:
    """Tests for _validate_header_scheme function."""

    def test_valid_bearer_token(self):
        """Test valid Bearer token extraction."""
        token = _validate_header_scheme("Bearer my-token-123")
        assert token == "my-token-123"

    def test_bearer_with_colon(self):
        """Test Bearer: format is accepted."""
        token = _validate_header_scheme("Bearer: my-token-123")
        assert token == "my-token-123"

    def test_case_insensitive_bearer(self):
        """Test that Bearer is case-insensitive."""
        token = _validate_header_scheme("bearer my-token-123")
        assert token == "my-token-123"

        token = _validate_header_scheme("BEARER my-token-123")
        assert token == "my-token-123"

    def test_invalid_format_single_part(self):
        """Test invalid format with single part."""
        with pytest.raises(HTTPException) as exc_info:
            _validate_header_scheme("InvalidFormat")

        assert exc_info.value.status_code == 401
        assert "Invalid Authorization header format" in exc_info.value.detail

    def test_invalid_format_three_parts(self):
        """Test invalid format with three parts."""
        with pytest.raises(HTTPException) as exc_info:
            _validate_header_scheme("Bearer token extra")

        assert exc_info.value.status_code == 401

    def test_wrong_scheme(self):
        """Test wrong authentication scheme."""
        with pytest.raises(HTTPException) as exc_info:
            _validate_header_scheme("Basic token123")

        assert exc_info.value.status_code == 401
        assert "Invalid authorization scheme" in exc_info.value.detail

    def test_empty_token(self):
        """Test empty token value - actually just tests malformed header."""
        with pytest.raises(HTTPException) as exc_info:
            _validate_header_scheme("Bearer")  # No token at all

        assert exc_info.value.status_code == 401
        # This will fail the format check, not the empty token check
        assert "Invalid Authorization header format" in exc_info.value.detail


class TestValidateAuthorizationHeader:
    """Tests for validate_authorization_header function."""

    def test_valid_token_success(self, monkeypatch):
        """Test successful validation with correct token."""
        test_token = "test-token-123"
        monkeypatch.setattr(settings, "api_token", test_token)

        result = validate_authorization_header(f"Bearer {test_token}")
        assert result == test_token

    def test_invalid_token_raises_401(self, monkeypatch):
        """Test that invalid token raises 401."""
        monkeypatch.setattr(settings, "api_token", "correct-token")

        with pytest.raises(HTTPException) as exc_info:
            validate_authorization_header("Bearer wrong-token")

        assert exc_info.value.status_code == 401
        assert "Invalid authentication token" in exc_info.value.detail

    def test_missing_header_raises_401(self):
        """Test that missing header raises 401."""
        with pytest.raises(HTTPException) as exc_info:
            validate_authorization_header(None)

        assert exc_info.value.status_code == 401
        assert "Missing Authorization header" in exc_info.value.detail

    def test_malformed_header_raises_401(self):
        """Test that malformed header raises 401."""
        with pytest.raises(HTTPException) as exc_info:
            validate_authorization_header("InvalidFormat")

        assert exc_info.value.status_code == 401

    def test_whitespace_handling(self, monkeypatch):
        """Test that extra whitespace is handled correctly."""
        test_token = "test-token-123"
        monkeypatch.setattr(settings, "api_token", test_token)

        # Extra spaces should be handled
        result = validate_authorization_header(f"Bearer  {test_token}  ")
        assert result == test_token

    def test_returns_www_authenticate_header(self):
        """Test that 401 responses include WWW-Authenticate header."""
        with pytest.raises(HTTPException) as exc_info:
            validate_authorization_header(None)

        assert "WWW-Authenticate" in exc_info.value.headers
        assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"
