"""Unit tests for Pydantic models."""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models import InsightRequest, InsightData, InsightResponse, HealthResponse


class TestInsightRequest:
    """Tests for InsightRequest model."""

    def test_valid_request(self):
        """Test creating valid InsightRequest."""
        request = InsightRequest(symbol="BTC")
        assert request.symbol == "BTC"

    def test_missing_symbol_raises_error(self):
        """Test that missing symbol raises validation error."""
        with pytest.raises(ValidationError):
            InsightRequest()

    def test_symbol_can_be_any_string(self):
        """Test that symbol accepts various string formats."""
        request1 = InsightRequest(symbol="BTC")
        request2 = InsightRequest(symbol="bitcoin")
        request3 = InsightRequest(symbol="BTC-USD")

        assert request1.symbol == "BTC"
        assert request2.symbol == "bitcoin"
        assert request3.symbol == "BTC-USD"


class TestInsightData:
    """Tests for InsightData model."""

    def test_valid_insight_data(self):
        """Test creating valid InsightData."""
        data = InsightData(
            symbol="bitcoin",
            name="Bitcoin",
            category="coin",
            description="First cryptocurrency",
            date_launched="2009-01-03"
        )

        assert data.symbol == "bitcoin"
        assert data.name == "Bitcoin"
        assert data.category == "coin"

    def test_optional_fields_can_be_none(self):
        """Test that optional fields can be None."""
        data = InsightData(
            symbol="bitcoin",
            name="Bitcoin",
            category="coin",
            description="Test",
            date_launched="2009-01-03",
            logo=None,
            platform=None,
            circulating_suply=None,
            market_cap=None
        )

        assert data.logo is None
        assert data.platform is None
        assert data.circulating_suply is None
        assert data.market_cap is None

    def test_optional_fields_with_values(self):
        """Test optional fields with values."""
        data = InsightData(
            symbol="ethereum",
            name="Ethereum",
            category="coin",
            description="Smart contract platform",
            date_launched="2015-07-30",
            logo="https://example.com/logo.png",
            platform="Ethereum",
            circulating_suply=120000000.0,
            market_cap=250000000000.0
        )

        assert data.logo == "https://example.com/logo.png"
        assert data.platform == "Ethereum"
        assert data.circulating_suply == 120000000.0
        assert data.market_cap == 250000000000.0

    def test_missing_required_fields_raises_error(self):
        """Test that missing required fields raises validation error."""
        with pytest.raises(ValidationError):
            InsightData(symbol="BTC")  # Missing other required fields


class TestInsightResponse:
    """Tests for InsightResponse model."""

    def test_valid_insight_response(self):
        """Test creating valid InsightResponse."""
        data = InsightData(
            symbol="bitcoin",
            name="Bitcoin",
            category="coin",
            description="Test",
            date_launched="2009-01-03"
        )

        response = InsightResponse(
            request_id="123e4567-e89b-12d3-a456-426614174000",
            symbol="BTC",
            data=data,
            cached=False,
            fetched_at=datetime.now()
        )

        assert response.request_id == "123e4567-e89b-12d3-a456-426614174000"
        assert response.symbol == "BTC"
        assert response.data == data
        assert response.cached is False
        assert isinstance(response.fetched_at, datetime)

    def test_cached_true(self):
        """Test cached field set to True."""
        data = InsightData(
            symbol="bitcoin",
            name="Bitcoin",
            category="coin",
            description="Test",
            date_launched="2009-01-03"
        )

        response = InsightResponse(
            request_id="test-id",
            symbol="BTC",
            data=data,
            cached=True,
            fetched_at=datetime.now()
        )

        assert response.cached is True

    def test_missing_required_fields_raises_error(self):
        """Test that missing required fields raises validation error."""
        with pytest.raises(ValidationError):
            InsightResponse(request_id="test-id")


class TestHealthResponse:
    """Tests for HealthResponse model."""

    def test_valid_health_response(self):
        """Test creating valid HealthResponse."""
        response = HealthResponse(
            status="healthy",
            timestamp=datetime.now()
        )

        assert response.status == "healthy"
        assert isinstance(response.timestamp, datetime)

    def test_degraded_status(self):
        """Test health response with degraded status."""
        response = HealthResponse(
            status="degraded",
            timestamp=datetime.now()
        )

        assert response.status == "degraded"

    def test_missing_fields_raises_error(self):
        """Test that missing fields raises validation error."""
        with pytest.raises(ValidationError):
            HealthResponse()

        with pytest.raises(ValidationError):
            HealthResponse(status="healthy")
