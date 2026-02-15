"""Unit tests for validators module."""
import pytest
from fastapi import HTTPException

from app.dependencies.validator import validate_symbol, ALLOWED_SYMBOLS


class TestValidateSymbol:
    """Test cases for validate_symbol function."""

    def test_validate_symbol_valid_lowercase(self):
        """Test validation with valid lowercase symbol."""
        result = validate_symbol("bitcoin")
        assert result == "bitcoin"

    def test_validate_symbol_valid_uppercase(self):
        """Test validation with valid uppercase symbol."""
        result = validate_symbol("BITCOIN")
        assert result == "bitcoin"

    def test_validate_symbol_valid_mixed_case(self):
        """Test validation with valid mixed case symbol."""
        result = validate_symbol("BiTcOiN")
        assert result == "bitcoin"

    def test_validate_symbol_with_whitespace(self):
        """Test validation strips whitespace."""
        result = validate_symbol("  bitcoin  ")
        assert result == "bitcoin"

    def test_validate_symbol_all_allowed_symbols(self):
        """Test all allowed symbols pass validation."""
        for symbol in ALLOWED_SYMBOLS:
            result = validate_symbol(symbol)
            assert result == symbol

    def test_validate_symbol_invalid_symbol_raises_exception(self):
        """Test invalid symbol raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            validate_symbol("invalidcoin")

        assert exc_info.value.status_code == 400
        assert "Invalid symbol" in exc_info.value.detail
        assert "bitcoin" in exc_info.value.detail  # Should list allowed symbols

    def test_validate_symbol_empty_string_raises_exception(self):
        """Test empty string raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            validate_symbol("")

        assert exc_info.value.status_code == 400

    def test_validate_symbol_whitespace_only_raises_exception(self):
        """Test whitespace-only string raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            validate_symbol("   ")

        assert exc_info.value.status_code == 400
