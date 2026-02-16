from fastapi import HTTPException, status
from httpx import (
    Client,
    TimeoutException,
    HTTPStatusError
)

from app.dependencies.logger import logger
from app.config import settings

def fetch_symbol_data(symbol: str) -> dict:
    """
    Fetch data from Fetcher service with timeout and error handling.

    Args:
        symbol: Cryptocurrency symbol

    Returns:
        Normalized data from Fetcher service

    Raises:
        HTTPException: If Fetcher service fails or times out
    """
    url = f"{settings.fetcher_url}/v1/fetch/symbol"
    params = {"symbol": symbol}

    logger.info(f"Calling Fetcher service: {url} with symbol={symbol}")

    try:
        with Client() as client:
            response = client.get(url, params=params, timeout=settings.fetcher_timeout)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Fetcher service responded successfully for symbol={symbol}")
            return data

    except TimeoutException:
        logger.error(f"Fetcher service timeout for symbol={symbol}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Fetcher service request timed out"
        )

    except HTTPStatusError as e:
        print(e)
        logger.error(f"Fetcher service HTTP error: {e.response.status_code}")
        if e.response.status_code >= 500:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Fetcher service is currently unavailable"
            )
        else:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Fetcher service error: {e.response.text}"
            )

    except Exception as e:
        logger.error(f"Unexpected error calling Fetcher service: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to communicate with Fetcher service"
        )