"""Unit tests for CoinMarketCap client."""
import pytest
from unittest.mock import AsyncMock, patch
import httpx
from fastapi import HTTPException

from app.dependencies.coinmarketcap_client import CoinMarketCapClient
from app.models import CryptoInsightOutput


class TestCoinMarketCapClientInit:
    """Test CoinMarketCapClient initialization."""

    def test_client_initialization(self, test_settings):
        """Test client initializes with correct attributes."""
        client = CoinMarketCapClient()
        assert client.base_url == test_settings["coinmarketcap_base_url"]
        assert client.api_key == test_settings["coinmarketcap_api_key"]
        assert client.timeout == 10.0


class TestValidateUrl:
    """Test URL validation for SSRF protection."""

    def test_validate_url_valid(self, test_settings):
        """Test valid URL passes validation."""
        client = CoinMarketCapClient()
        url = f"{test_settings['coinmarketcap_base_url']}/cryptocurrency/info?slug=bitcoin"
        # Should not raise exception
        client._validate_url(url)

    def test_validate_url_with_query_params(self, test_settings):
        """Test valid URL with query params passes validation."""
        client = CoinMarketCapClient()
        url = f"{test_settings['coinmarketcap_base_url']}/cryptocurrency/info?slug=cardano"
        # Should not raise exception
        client._validate_url(url)

    def test_validate_url_invalid_base_url_raises_error(self):
        """Test invalid base URL raises ValueError."""
        client = CoinMarketCapClient()
        url = "https://evil.com/api/v2/cryptocurrency/info"

        with pytest.raises(ValueError) as exc_info:
            client._validate_url(url)

        assert "SSRF protection" in str(exc_info.value)

    def test_validate_url_different_domain_raises_error(self):
        """Test different domain raises ValueError."""
        client = CoinMarketCapClient()
        url = "https://api.example.com/v2/cryptocurrency/info"

        with pytest.raises(ValueError) as exc_info:
            client._validate_url(url)

        assert "SSRF protection" in str(exc_info.value)

    def test_validate_url_localhost_rejected(self):
        """Test localhost URLs are rejected for SSRF protection."""
        client = CoinMarketCapClient()
        url = "http://localhost:8000/admin"

        with pytest.raises(ValueError) as exc_info:
            client._validate_url(url)

        assert "SSRF protection" in str(exc_info.value)

    def test_validate_url_internal_ip_rejected(self):
        """Test internal IP addresses are rejected for SSRF protection."""
        client = CoinMarketCapClient()
        url = "http://192.168.1.1/api"

        with pytest.raises(ValueError) as exc_info:
            client._validate_url(url)

        assert "SSRF protection" in str(exc_info.value)


class TestFetchWithRetry:
    """Test retry logic for fetching data."""

    @pytest.mark.asyncio
    async def test_fetch_with_retry_success(self, coinmarketcap_info_response_bitcoin):
        """Test successful fetch returns data using fixture."""
        client = CoinMarketCapClient()
        mock_response = AsyncMock()
        mock_response.json = lambda: coinmarketcap_info_response_bitcoin
        mock_response.raise_for_status = lambda: None

        with patch('httpx.AsyncClient') as mock_async_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_async_client.return_value.__aenter__.return_value = mock_client_instance

            url = f"{client.base_url}/cryptocurrency/info?slug=bitcoin"
            headers = {"X-CMC_PRO_API_KEY": client.api_key}

            result = await client._fetch_with_retry(url, headers)

            assert result == coinmarketcap_info_response_bitcoin
            mock_client_instance.get.assert_called_once_with(url, headers=headers)

    @pytest.mark.asyncio
    async def test_fetch_with_retry_http_error(self):
        """Test HTTP error is raised after retries."""
        client = CoinMarketCapClient()
        mock_response = AsyncMock()
        mock_response.status_code = 500

        def raise_http_error():
            raise httpx.HTTPStatusError(
                "Server error", request=AsyncMock(), response=mock_response
            )

        mock_response.raise_for_status = raise_http_error

        with patch('httpx.AsyncClient') as mock_async_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_async_client.return_value.__aenter__.return_value = mock_client_instance

            url = f"{client.base_url}/cryptocurrency/info?slug=bitcoin"
            headers = {"X-CMC_PRO_API_KEY": client.api_key}

            with pytest.raises(httpx.HTTPStatusError):
                await client._fetch_with_retry(url, headers)

            # Should retry 3 times
            assert mock_client_instance.get.call_count == 3

    @pytest.mark.asyncio
    async def test_fetch_with_retry_connection_error(self):
        """Test connection error is raised after retries."""
        client = CoinMarketCapClient()
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.get.side_effect = httpx.RequestError("Connection failed")
            mock_async_client.return_value.__aenter__.return_value = mock_client_instance

            url = f"{client.base_url}/cryptocurrency/info?slug=bitcoin"
            headers = {"X-CMC_PRO_API_KEY": client.api_key}

            with pytest.raises(httpx.RequestError):
                await client._fetch_with_retry(url, headers)

            # Should retry 3 times
            assert mock_client_instance.get.call_count == 3


class TestFetchCoinData:
    """Test fetching cryptocurrency data."""

    @pytest.mark.asyncio
    async def test_fetch_coin_data_success_bitcoin(self, coinmarketcap_info_response_bitcoin):
        """Test successful fetch returns CryptoInsightOutput using fixture."""
        client = CoinMarketCapClient()

        with patch.object(client, '_fetch_with_retry', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = coinmarketcap_info_response_bitcoin

            result = await client.fetch_coin_data("bitcoin")

            assert isinstance(result, CryptoInsightOutput)
            assert result.symbol == "bitcoin"
            assert result.name == "Bitcoin"
            assert result.category == "coin"
            assert result.description == "Bitcoin (BTC) is a cryptocurrency. Bitcoin is the original cryptocurrency."
            assert result.date_launched == "2009-01-03T00:00:00.000Z"
            assert result.logo == "https://s2.coinmarketcap.com/static/img/coins/64x64/1.png"
            assert result.platform is None
            assert result.circulating_suply == 19500000.0
            assert result.market_cap == 885000000000.0

    @pytest.mark.asyncio
    async def test_fetch_coin_data_success_with_platform(self, coinmarketcap_info_response_with_platform):
        """Test successful fetch of token with platform information using fixture."""
        client = CoinMarketCapClient()

        with patch.object(client, '_fetch_with_retry', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = coinmarketcap_info_response_with_platform

            result = await client.fetch_coin_data("cardano")

            assert isinstance(result, CryptoInsightOutput)
            assert result.symbol == "cardano"
            assert result.name == "Cardano"
            assert result.platform == "Ethereum"
            assert result.circulating_suply == 33000000000.0
            assert result.market_cap == 16500000000.0

    @pytest.mark.asyncio
    async def test_fetch_coin_data_constructs_correct_url(self, coinmarketcap_info_response_bitcoin):
        """Test correct URL is constructed using fixture."""
        client = CoinMarketCapClient()

        with patch.object(client, '_fetch_with_retry', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = coinmarketcap_info_response_bitcoin

            await client.fetch_coin_data("bitcoin")

            # Verify URL was constructed correctly
            call_args = mock_fetch.call_args
            url = call_args[0][0]
            assert "cryptocurrency/info?slug=bitcoin" in url

    @pytest.mark.asyncio
    async def test_fetch_coin_data_includes_api_key_header(self, coinmarketcap_info_response_bitcoin, test_settings):
        """Test API key is included in headers using fixture."""
        client = CoinMarketCapClient()

        with patch.object(client, '_fetch_with_retry', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = coinmarketcap_info_response_bitcoin

            await client.fetch_coin_data("bitcoin")

            # Verify headers include API key
            call_args = mock_fetch.call_args
            headers = call_args[0][1]
            assert headers["X-CMC_PRO_API_KEY"] == test_settings["coinmarketcap_api_key"]
            assert headers["Accept"] == "application/json"

    @pytest.mark.asyncio
    async def test_fetch_coin_data_http_400_error(self):
        """Test HTTP 400 error raises appropriate HTTPException."""
        client = CoinMarketCapClient()
        mock_response = AsyncMock()
        mock_response.status_code = 400

        error = httpx.HTTPStatusError("Bad request", request=AsyncMock(), response=mock_response)

        with patch.object(client, '_fetch_with_retry', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = error

            with pytest.raises(HTTPException) as exc_info:
                await client.fetch_coin_data("bitcoin")

            assert exc_info.value.status_code == 400
            assert "Invalid request" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_fetch_coin_data_http_401_error(self):
        """Test HTTP 401 error raises appropriate HTTPException."""
        client = CoinMarketCapClient()
        mock_response = AsyncMock()
        mock_response.status_code = 401

        error = httpx.HTTPStatusError("Unauthorized", request=AsyncMock(), response=mock_response)

        with patch.object(client, '_fetch_with_retry', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = error

            with pytest.raises(HTTPException) as exc_info:
                await client.fetch_coin_data("bitcoin")

            assert exc_info.value.status_code == 503
            assert "authentication failed" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_fetch_coin_data_http_404_error(self):
        """Test HTTP 404 error raises appropriate HTTPException."""
        client = CoinMarketCapClient()
        mock_response = AsyncMock()
        mock_response.status_code = 404

        error = httpx.HTTPStatusError("Not found", request=AsyncMock(), response=mock_response)

        with patch.object(client, '_fetch_with_retry', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = error

            with pytest.raises(HTTPException) as exc_info:
                await client.fetch_coin_data("bitcoin")

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_fetch_coin_data_http_500_error(self):
        """Test HTTP 500 error raises appropriate HTTPException."""
        client = CoinMarketCapClient()
        mock_response = AsyncMock()
        mock_response.status_code = 500

        error = httpx.HTTPStatusError("Server error", request=AsyncMock(), response=mock_response)

        with patch.object(client, '_fetch_with_retry', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = error

            with pytest.raises(HTTPException) as exc_info:
                await client.fetch_coin_data("bitcoin")

            assert exc_info.value.status_code == 503
            assert "unavailable" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_fetch_coin_data_connection_error(self):
        """Test connection error raises appropriate HTTPException."""
        client = CoinMarketCapClient()
        error = httpx.RequestError("Connection failed")

        with patch.object(client, '_fetch_with_retry', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = error

            with pytest.raises(HTTPException) as exc_info:
                await client.fetch_coin_data("bitcoin")

            assert exc_info.value.status_code == 503
            assert "Failed to connect" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_fetch_coin_data_empty_data(self, empty_data_response):
        """Test empty data response raises HTTPException using fixture."""
        client = CoinMarketCapClient()

        with patch.object(client, '_fetch_with_retry', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = empty_data_response

            with pytest.raises(HTTPException) as exc_info:
                await client.fetch_coin_data("unknown")

            assert exc_info.value.status_code == 500
            assert "Failed to parse" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_fetch_coin_data_missing_symbol_in_response(self, coinmarketcap_info_response_bitcoin):
        """Test missing requested symbol in response raises HTTPException."""
        client = CoinMarketCapClient()

        with patch.object(client, '_fetch_with_retry', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = coinmarketcap_info_response_bitcoin

            # Request ethereum but get bitcoin data
            with pytest.raises(HTTPException) as exc_info:
                await client.fetch_coin_data("ethereum")

            assert exc_info.value.status_code == 500
            assert "Failed to parse" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_fetch_coin_data_missing_required_fields(self, missing_fields_response):
        """Test missing required fields raises HTTPException using fixture."""
        client = CoinMarketCapClient()

        with patch.object(client, '_fetch_with_retry', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = missing_fields_response

            with pytest.raises(HTTPException) as exc_info:
                await client.fetch_coin_data("bitcoin")

            assert exc_info.value.status_code == 500
            assert "Failed to parse" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_fetch_coin_data_url_validation_called(self, coinmarketcap_info_response_bitcoin):
        """Test that URL validation is called to prevent SSRF."""
        client = CoinMarketCapClient()

        with patch.object(client, '_validate_url') as mock_validate:
            with patch.object(client, '_fetch_with_retry', new_callable=AsyncMock) as mock_fetch:
                mock_fetch.return_value = coinmarketcap_info_response_bitcoin

                await client.fetch_coin_data("bitcoin")

                # Verify URL validation was called
                mock_validate.assert_called_once()
                called_url = mock_validate.call_args[0][0]
                assert "cryptocurrency/info?slug=bitcoin" in called_url
