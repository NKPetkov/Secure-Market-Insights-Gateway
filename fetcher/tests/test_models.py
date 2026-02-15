"""Unit tests for data models."""
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from app.models import CryptoInsightOutput, HealthResponse


class TestCryptoInsightOutput:
    """Test cases for CryptoInsightOutput model."""

    def test_crypto_insight_output_valid_data(self):
        """Test CryptoInsightOutput creation with valid data."""
        data = {
            "symbol": "bitcoin",
            "name": "Bitcoin",
            "category": "coin",
            "description": "Bitcoin is a cryptocurrency",
            "date_launched": "2009-01-03T00:00:00.000Z",
            "logo": "https://example.com/logo.png",
            "platform": None,
            "circulating_suply": 19500000.0,
            "market_cap": 885000000000.0
        }

        insight = CryptoInsightOutput(**data)

        assert insight.symbol == "bitcoin"
        assert insight.name == "Bitcoin"
        assert insight.category == "coin"
        assert insight.description == "Bitcoin is a cryptocurrency"
        assert insight.date_launched == "2009-01-03T00:00:00.000Z"
        assert insight.logo == "https://example.com/logo.png"
        assert insight.platform is None
        assert insight.circulating_suply == 19500000.0
        assert insight.market_cap == 885000000000.0

    def test_crypto_insight_output_with_platform(self):
        """Test CryptoInsightOutput with platform information."""
        data = {
            "symbol": "cardano",
            "name": "Cardano",
            "category": "coin",
            "description": "Cardano is a proof-of-stake blockchain",
            "date_launched": "2017-09-29T00:00:00.000Z",
            "logo": "https://example.com/cardano.png",
            "platform": "Ethereum",
            "circulating_suply": 33000000000.0,
            "market_cap": 16500000000.0
        }

        insight = CryptoInsightOutput(**data)
        assert insight.platform == "Ethereum"

    def test_crypto_insight_output_missing_required_field(self):
        """Test CryptoInsightOutput raises error when required field is missing."""
        data = {
            "symbol": "bitcoin",
            "name": "Bitcoin",
            # Missing category
            "description": "Bitcoin is a cryptocurrency",
            "date_launched": "2009-01-03T00:00:00.000Z"
        }

        with pytest.raises(ValidationError):
            CryptoInsightOutput(**data)

    def test_crypto_insight_output_optional_fields_none(self):
        """Test CryptoInsightOutput accepts None for optional fields."""
        data = {
            "symbol": "bitcoin",
            "name": "Bitcoin",
            "category": "coin",
            "description": "Bitcoin is a cryptocurrency",
            "date_launched": "2009-01-03T00:00:00.000Z",
            "logo": None,
            "platform": None,
            "circulating_suply": None,
            "market_cap": None
        }

        insight = CryptoInsightOutput(**data)
        assert insight.logo is None
        assert insight.platform is None
        assert insight.circulating_suply is None
        assert insight.market_cap is None

    def test_crypto_insight_output_zero_market_cap(self):
        """Test CryptoInsightOutput accepts zero market cap."""
        data = {
            "symbol": "bitcoin",
            "name": "Bitcoin",
            "category": "coin",
            "description": "Bitcoin is a cryptocurrency",
            "date_launched": "2009-01-03T00:00:00.000Z",
            "circulating_suply": 1000000.0,
            "market_cap": 0.0
        }

        insight = CryptoInsightOutput(**data)
        assert insight.market_cap == 0.0

    def test_crypto_insight_output_serialization(self):
        """Test CryptoInsightOutput can be serialized to dict."""
        data = {
            "symbol": "bitcoin",
            "name": "Bitcoin",
            "category": "coin",
            "description": "Bitcoin is a cryptocurrency",
            "date_launched": "2009-01-03T00:00:00.000Z",
            "circulating_suply": 19500000.0,
            "market_cap": 885000000000.0
        }

        insight = CryptoInsightOutput(**data)
        serialized = insight.model_dump()

        assert isinstance(serialized, dict)
        assert serialized["symbol"] == "bitcoin"
        assert serialized["name"] == "Bitcoin"
        assert serialized["category"] == "coin"

    def test_crypto_insight_output_json_serialization(self):
        """Test CryptoInsightOutput can be serialized to JSON."""
        data = {
            "symbol": "bitcoin",
            "name": "Bitcoin",
            "category": "coin",
            "description": "Bitcoin is a cryptocurrency",
            "date_launched": "2009-01-03T00:00:00.000Z",
            "circulating_suply": 19500000.0,
            "market_cap": 885000000000.0
        }

        insight = CryptoInsightOutput(**data)
        json_str = insight.model_dump_json()

        assert isinstance(json_str, str)
        assert "bitcoin" in json_str
        assert "Bitcoin" in json_str
        assert "coin" in json_str

    def test_crypto_insight_output_large_numbers(self):
        """Test CryptoInsightOutput handles large numbers correctly."""
        data = {
            "symbol": "bitcoin",
            "name": "Bitcoin",
            "category": "coin",
            "description": "Bitcoin is a cryptocurrency",
            "date_launched": "2009-01-03T00:00:00.000Z",
            "circulating_suply": 999999999999.99,
            "market_cap": 99999999999999.99
        }

        insight = CryptoInsightOutput(**data)
        assert insight.circulating_suply == 999999999999.99
        assert insight.market_cap == 99999999999999.99

    def test_crypto_insight_output_decimal_precision(self):
        """Test CryptoInsightOutput maintains decimal precision."""
        data = {
            "symbol": "bitcoin",
            "name": "Bitcoin",
            "category": "coin",
            "description": "Bitcoin is a cryptocurrency",
            "date_launched": "2009-01-03T00:00:00.000Z",
            "circulating_suply": 19500000.123456789,
            "market_cap": 885000000000.987654321
        }

        insight = CryptoInsightOutput(**data)
        # Float precision may vary slightly
        assert abs(insight.circulating_suply - 19500000.123456789) < 0.0001


class TestHealthResponse:
    """Test cases for HealthResponse model."""

    def test_health_response_valid_data(self):
        """Test HealthResponse creation with valid data."""
        data = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc)
        }

        response = HealthResponse(**data)

        assert response.status == "healthy"
        assert isinstance(response.timestamp, datetime)

    def test_health_response_missing_status(self):
        """Test HealthResponse requires status field."""
        data = {
            "timestamp": datetime.now(timezone.utc)
        }

        with pytest.raises(ValidationError):
            HealthResponse(**data)

    def test_health_response_missing_timestamp(self):
        """Test HealthResponse requires timestamp field."""
        data = {
            "status": "healthy"
        }

        with pytest.raises(ValidationError):
            HealthResponse(**data)

    def test_health_response_invalid_timestamp_type(self):
        """Test HealthResponse validates timestamp type."""
        data = {
            "status": "healthy",
            "timestamp": "not-a-datetime"
        }

        with pytest.raises(ValidationError):
            HealthResponse(**data)

    def test_health_response_different_status_values(self):
        """Test HealthResponse accepts different status values."""
        statuses = ["healthy", "unhealthy", "degraded", "starting"]

        for status_value in statuses:
            data = {
                "status": status_value,
                "timestamp": datetime.now(timezone.utc)
            }

            response = HealthResponse(**data)
            assert response.status == status_value

    def test_health_response_serialization(self):
        """Test HealthResponse can be serialized to dict."""
        data = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc)
        }

        response = HealthResponse(**data)
        serialized = response.model_dump()

        assert isinstance(serialized, dict)
        assert serialized["status"] == "healthy"
        assert "timestamp" in serialized

    def test_health_response_json_serialization(self):
        """Test HealthResponse can be serialized to JSON."""
        data = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc)
        }

        response = HealthResponse(**data)
        json_str = response.model_dump_json()

        assert isinstance(json_str, str)
        assert "healthy" in json_str
