"""Unit tests for fetch route."""
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.models import CryptoInsightOutput


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestFetchEndpoint:
    """Test cases for crypto data fetch endpoint."""

    def test_fetch_requires_symbol_parameter(self, client):
        """Test fetch endpoint requires symbol query parameter."""
        response = client.get("/v1/fetch")
        assert response.status_code == 422  # Validation error

    def test_fetch_with_valid_symbol_returns_200(self, client, coinmarketcap_info_response_bitcoin):
        """Test fetch with valid symbol returns 200 OK using fixture."""
        mock_insight = CryptoInsightOutput(
            symbol="bitcoin",
            name="Bitcoin",
            category="coin",
            description="Bitcoin (BTC) is a cryptocurrency. Bitcoin is the original cryptocurrency.",
            date_launched="2009-01-03T00:00:00.000Z",
            logo="https://s2.coinmarketcap.com/static/img/coins/64x64/1.png",
            platform=None,
            circulating_suply=19500000.0,
            market_cap=885000000000.0
        )

        with patch('app.routers.fetch.coinmarketcap_client.fetch_coin_data', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_insight

            response = client.get("/v1/fetch?symbol=bitcoin")
            assert response.status_code == 200

    def test_fetch_with_invalid_symbol_returns_400(self, client):
        """Test fetch with invalid symbol returns 400."""
        response = client.get("/v1/fetch?symbol=invalidcoin")
        assert response.status_code == 400

        data = response.json()
        assert "Invalid symbol" in data["detail"]

    def test_fetch_returns_correct_data_structure(self, client):
        """Test fetch returns correct JSON structure using fixture."""
        mock_insight = CryptoInsightOutput(
            symbol="bitcoin",
            name="Bitcoin",
            category="coin",
            description="Bitcoin description",
            date_launched="2009-01-03T00:00:00.000Z",
            circulating_suply=19500000.0,
            market_cap=885000000000.0
        )

        with patch('app.routers.fetch.coinmarketcap_client.fetch_coin_data', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_insight

            response = client.get("/v1/fetch?symbol=bitcoin")
            data = response.json()

            assert "symbol" in data
            assert "name" in data
            assert "category" in data
            assert "description" in data
            assert "date_launched" in data
            assert "circulating_suply" in data
            assert "market_cap" in data

    def test_fetch_returns_correct_values(self, client):
        """Test fetch returns correct values using fixture."""
        mock_insight = CryptoInsightOutput(
            symbol="bitcoin",
            name="Bitcoin",
            category="coin",
            description="Bitcoin description",
            date_launched="2009-01-03T00:00:00.000Z",
            circulating_suply=19500000.0,
            market_cap=885000000000.0
        )

        with patch('app.routers.fetch.coinmarketcap_client.fetch_coin_data', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_insight

            response = client.get("/v1/fetch?symbol=bitcoin")
            data = response.json()

            assert data["symbol"] == "bitcoin"
            assert data["name"] == "Bitcoin"
            assert data["category"] == "coin"
            assert data["circulating_suply"] == 19500000.0
            assert data["market_cap"] == 885000000000.0

    def test_fetch_all_allowed_symbols(self, client):
        """Test fetch works for all allowed symbols using dynamic fixtures."""
        allowed_symbols = ["bitcoin", "ethereum", "cardano", "solana", "polkadot"]

        for symbol in allowed_symbols:
            mock_insight = CryptoInsightOutput(
                symbol=symbol,
                name=symbol.capitalize(),
                category="coin",
                description=f"{symbol.capitalize()} description",
                date_launched="2009-01-03T00:00:00.000Z",
                circulating_suply=1000000.0,
                market_cap=1000000000.0
            )

            with patch('app.routers.fetch.coinmarketcap_client.fetch_coin_data', new_callable=AsyncMock) as mock_fetch:
                mock_fetch.return_value = mock_insight

                response = client.get(f"/v1/fetch?symbol={symbol}")
                assert response.status_code == 200

    def test_fetch_symbol_case_insensitive(self, client):
        """Test fetch endpoint is case insensitive."""
        test_cases = ["bitcoin", "BITCOIN", "BiTcOiN"]
        mock_insight = CryptoInsightOutput(
            symbol="bitcoin",
            name="Bitcoin",
            category="coin",
            description="Bitcoin description",
            date_launched="2009-01-03T00:00:00.000Z",
            circulating_suply=19500000.0,
            market_cap=885000000000.0
        )

        for symbol in test_cases:
            with patch('app.routers.fetch.coinmarketcap_client.fetch_coin_data', new_callable=AsyncMock) as mock_fetch:
                mock_fetch.return_value = mock_insight

                response = client.get(f"/v1/fetch?symbol={symbol}")
                assert response.status_code == 200

    def test_fetch_handles_upstream_503_error(self, client):
        """Test fetch handles upstream service unavailable error."""
        from fastapi import HTTPException as FE
        with patch('app.routers.fetch.coinmarketcap_client.fetch_coin_data', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = FE(
                status_code=503,
                detail="Upstream API unavailable"
            )

            response = client.get("/v1/fetch?symbol=bitcoin")
            assert response.status_code == 503

    def test_fetch_handles_upstream_404_error(self, client):
        """Test fetch handles not found error."""
        from fastapi import HTTPException as FE
        with patch('app.routers.fetch.coinmarketcap_client.fetch_coin_data', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = FE(
                status_code=404,
                detail="Cryptocurrency not found"
            )

            response = client.get("/v1/fetch?symbol=bitcoin")
            assert response.status_code == 404

    def test_fetch_handles_parsing_error(self, client):
        """Test fetch handles data parsing error."""
        from fastapi import HTTPException as FE
        with patch('app.routers.fetch.coinmarketcap_client.fetch_coin_data', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = FE(
                status_code=500,
                detail="Failed to parse upstream API response"
            )

            response = client.get("/v1/fetch?symbol=bitcoin")
            assert response.status_code == 500

    def test_fetch_content_type(self, client):
        """Test fetch returns JSON content type."""
        mock_insight = CryptoInsightOutput(
            symbol="bitcoin",
            name="Bitcoin",
            category="coin",
            description="Bitcoin description",
            date_launched="2009-01-03T00:00:00.000Z",
            circulating_suply=19500000.0,
            market_cap=885000000000.0
        )

        with patch('app.routers.fetch.coinmarketcap_client.fetch_coin_data', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_insight

            response = client.get("/v1/fetch?symbol=bitcoin")
            assert "application/json" in response.headers["content-type"]

    def test_fetch_with_whitespace_in_symbol(self, client):
        """Test fetch handles whitespace in symbol."""
        mock_insight = CryptoInsightOutput(
            symbol="bitcoin",
            name="Bitcoin",
            category="coin",
            description="Bitcoin description",
            date_launched="2009-01-03T00:00:00.000Z",
            circulating_suply=19500000.0,
            market_cap=885000000000.0
        )

        with patch('app.routers.fetch.coinmarketcap_client.fetch_coin_data', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_insight

            response = client.get("/v1/fetch?symbol=%20bitcoin%20")  # URL encoded spaces
            assert response.status_code == 200

    def test_fetch_calls_client_with_validated_symbol(self, client):
        """Test fetch calls client with validated lowercase symbol."""
        mock_insight = CryptoInsightOutput(
            symbol="bitcoin",
            name="Bitcoin",
            category="coin",
            description="Bitcoin description",
            date_launched="2009-01-03T00:00:00.000Z",
            circulating_suply=19500000.0,
            market_cap=885000000000.0
        )

        with patch('app.routers.fetch.coinmarketcap_client.fetch_coin_data', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_insight

            client.get("/v1/fetch?symbol=BITCOIN")

            # Verify client was called with lowercase symbol
            mock_fetch.assert_called_once_with("bitcoin")

    def test_fetch_multiple_concurrent_requests(self, client):
        """Test fetch can handle multiple requests."""
        mock_insight = CryptoInsightOutput(
            symbol="bitcoin",
            name="Bitcoin",
            category="coin",
            description="Bitcoin description",
            date_launched="2009-01-03T00:00:00.000Z",
            circulating_suply=19500000.0,
            market_cap=885000000000.0
        )

        with patch('app.routers.fetch.coinmarketcap_client.fetch_coin_data', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_insight

            for i in range(10):
                response = client.get("/v1/fetch?symbol=bitcoin")
                assert response.status_code == 200

    def test_fetch_error_detail_format(self, client):
        """Test fetch error responses have correct detail format."""
        response = client.get("/v1/fetch?symbol=invalidcoin")
        data = response.json()

        assert "detail" in data
        assert isinstance(data["detail"], str)
        assert len(data["detail"]) > 0
