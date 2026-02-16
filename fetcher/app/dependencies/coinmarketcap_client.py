"""CoinMarketCap API client"""
from typing import Dict, Any

from httpx import (
    Client,
    HTTPStatusError,
    RequestError
)
from httpx_retries import Retry, RetryTransport
from fastapi import HTTPException, status

from app.dependencies.logger import logger
from app.config import settings
from app.models import CryptoInsightOutput


class CoinMarketCapClient:
    """Client for fetching cryptocurrency data from CoinMarketCap API."""

    def __init__(self):
        """Initialize the CoinMarketCap client."""
        self.base_url = settings.coinmarketcap_base_url
        self.api_key = settings.coinmarketcap_api_key
        self.timeout = float(settings.outside_request_timeout)  # 10 seconds timeout (float for httpx)

    def _validate_url(self, url: str) -> None:
        """
        Validate URL to prevent SSRF attacks.

        Args:
            url: URL to validate

        Raises:
            ValueError: If URL doesn't start with allowed base URL
        """
        if not url.startswith(self.base_url):
            raise ValueError(
                f"SSRF protection: URL must start with {self.base_url}"
            )


    def _fetch_with_retry(self, url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Fetch data with retry logic.

        Args:
            url: URL to fetch
            headers: HTTP headers including API key

        Returns:
            JSON response data

        Raises:
            httpx.HTTPStatusError: If HTTP error occurs after retries
            httpx.RequestError: If connection error occurs after retries
        """
        retry = Retry(total=3, backoff_factor=0.5)
        transport = RetryTransport(retry=retry)

        with Client(transport=transport) as client:
            logger.info(f"Fetching data from CoinMarketCap: {url}")
            response = client.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()


    def fetch_coin_data(self, symbol: str) -> CryptoInsightOutput:
        """
        Fetch cryptocurrency data from CoinMarketCap API.

        Args:
            symbol: Cryptocurrency symbol name (e.g., 'bitcoin')

        Returns:
            Normalized CryptoInsightOutput data

        Raises:
            HTTPException: If API call fails or data is invalid
        """

        # Build URL for CoinMarketCap quotes endpoint
        url = f"{self.base_url}/cryptocurrency/info?slug={symbol}"

        # SSRF protection: validate URL
        self._validate_url(url)

        # Prepare headers with API key
        headers = {
            "X-CMC_PRO_API_KEY": self.api_key,
            "Accept": "application/json"
        }

        try:
            data = self._fetch_with_retry(url, headers)

            # CoinMarketCap response structure:
            # {
            #   "data": {
            #     "{symbol}": {
            #          ...
            #       }
            #     }
            #   }
            # }

            # Extract symbol data
            crypto_data = data.get("data", {}).get(symbol)
            if not crypto_data:
                raise ValueError(f"No data found for {symbol}")

            market_cap = crypto_data.get("self_reported_market_cap")
            circulating_suply = crypto_data.get("self_reported_circulating_supply")

            # Validate required fields
            if circulating_suply is None or market_cap is None:
                raise ValueError("Missing required market data fields")
            
            platform= crypto_data.get("platform", None)

            if platform:
                platform = platform.get("name", None)

            # Create normalized response
            insight = CryptoInsightOutput(
                symbol=symbol,
                name=crypto_data.get("name", symbol.capitalize()),
                category=crypto_data.get("category", None),
                description=crypto_data.get("description", None),
                date_launched=crypto_data.get("date_launched", None),
                logo=crypto_data.get("logo", None),
                platform=platform,
                circulating_suply=float(circulating_suply),
                market_cap=float(market_cap)
            )

            logger.info(f"Successfully fetched data for {symbol} ({symbol})")
            return insight

        except HTTPStatusError as e:
            logger.error(f"HTTP error fetching {symbol}: {e.response.status_code}")
            if e.response.status_code == 400:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid request for cryptocurrency '{symbol}'"
                )
            elif e.response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Upstream API authentication failed"
                )
            elif e.response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Cryptocurrency '{symbol}' not found"
                )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Upstream API unavailable"
            )

        except RequestError as e:
            logger.error(f"Connection error fetching {symbol}: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to connect to upstream API"
            )

        except (ValueError, KeyError) as e:
            logger.error(f"Data parsing error for {symbol}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to parse upstream API response"
            )


# Singleton instance
coinmarketcap_client = CoinMarketCapClient()
