import time
from fastapi import APIRouter, status, Query
from typing import Annotated
from ..models import CryptoInsightInput, CryptoInsightOutput
from ..dependencies.coinmarketcap_client import coinmarketcap_client
from ..dependencies.validator import validate_symbol
from ..dependencies.logger import logger

app = APIRouter(prefix="/v1/fetch", tags=["fetch"])


@app.get("/", response_model=CryptoInsightOutput, status_code=status.HTTP_200_OK)
async def fetch_symbol_data(symbol: Annotated[CryptoInsightInput, Query]):
    """
    Fetch cryptocurrency data from CoinMarketCap API.

    Args:
        symbol(CryptoInsightInput): Cryptocurrency symbol to fetch

    Returns:
        Normalized CryptoInsightOutput data

    Raises:
        HTTPException: 400 for invalid symbol, 503 for upstream failures
    """
    start_time = time.time()

    # Validate symbol against whitelist
    validated_symbol = validate_symbol(symbol)

    logger.info(f"Fetching data for symbol: {validated_symbol}")

    try:
        # Fetch data from CoinMarketCap
        insight = await coinmarketcap_client.fetch_coin_data(validated_symbol)

        duration = time.time() - start_time
        logger.info(
            f"Successfully fetched {validated_symbol} in {duration:.2f}s"
        )

        return insight

    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"Failed to fetch {validated_symbol} after {duration:.2f}s: {str(e)}"
        )
        raise