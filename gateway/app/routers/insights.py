import uuid, time
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status

from app.models import (
    InsightRequest,
    InsightResponse,
    InsightData
)

from app.dependencies.auth import verify_token
from app.dependencies.rate_limiter import rate_limit
from app.dependencies.cache import cache
from app.dependencies.logger import logger
from app.dependencies.validator import validate_symbol
from app.dependencies.fetcher_handler import fetch_symbol_data

app = APIRouter(prefix="/v1/insights", tags=["insights"])

@app.post("/", response_model=InsightResponse, tags=["Insights"])
@rate_limit()
def create_insight(
    insight_request: InsightRequest,
    token: str = Depends(verify_token)
):
    """
    Create a new insight request for a cryptocurrency symbol.

    This endpoint:
    - Validates authentication
    - Checks rate limits (via @rate_limit decorator)
    - Validates input symbol
    - Returns cached data if available
    - Fetches fresh data from Fetcher service if needed
    - Caches the result

    Args:
        insight_request: Insight request payload
        token: Validated authentication token

    Returns:
        Market insights data for the requested symbol
    """

    # Validate symbol
    symbol = validate_symbol(insight_request.symbol)

    # Create query params key for cache lookup
    query_params = f"symbol={symbol}"

    logger.info(f"Insight request for symbol={symbol}")

    # Check cache (two-level: query_params -> request_id -> data)
    cached_result = cache.get(query_params)

    if cached_result:
        cached_data, cached_request_id = cached_result
        logger.info(f"Returning cached data for {query_params} (request_id: {cached_request_id})")

        # Add fetched_at timestamp to cached data
        fetched_at = datetime.fromisoformat(cached_data.get("fetched_at"))

        return InsightResponse(
            request_id=cached_request_id,
            symbol=symbol,
            data=InsightData(**cached_data["data"]),
            cached=True,
            fetched_at=fetched_at
        )

    # Generate new request ID for this request
    request_id = str(uuid.uuid4())

    # Fetch from Fetcher service
    symbol_data = fetch_symbol_data(symbol)

    # Extract and validate data
    try:
        insight_data = InsightData(**symbol_data)
    except Exception as e:
        logger.error(f"Failed to parse Fetcher service response: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid data format from Fetcher service"
        )

    # Prepare cache data structure
    fetched_at = time.time()
    cache_data = {
        "data": symbol_data,
        "fetched_at": fetched_at
    }

    # Cache with two-level structure: query_params -> request_id, request_id -> data
    cache.set(query_params, request_id, cache_data)

    logger.info(f"Successfully processed insight request {request_id} for symbol={symbol}")

    return InsightResponse(
        request_id=request_id,
        symbol=symbol,
        data=insight_data,
        cached=False,
        fetched_at=fetched_at
    )


@app.get("/{request_id}", response_model=InsightResponse, tags=["Insights"])
@rate_limit(max_calls=20) # 20 calls per minute
async def get_insight(
    request_id: str,
    token: str = Depends(verify_token)
):
    """
    Retrieve a cached insight by request ID.

    This endpoint allows retrieving previously fetched insights from cache
    using the request_id returned from POST /v1/insights.

    Args:
        request_id: Request identifier from previous request
        symbol: Cryptocurrency symbol (for validation and response)
        token: Validated authentication token

    Returns:
        Cached market insights data
    """
    logger.info(f"Retrieving cached insight by request_id: {request_id}")

    # Lookup by request_id directly
    cached_data = cache.get_by_request_id(request_id)

    if not cached_data:
        logger.warning(f"No cached data found for request_id: {request_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No cached insights found for request_id '{request_id}'"
        )

    # Extract fetched_at timestamp
    fetched_at = datetime.fromisoformat(cached_data.get("fetched_at"))

    return InsightResponse(
        request_id=request_id,
        symbol=cached_data["data"]['symbol'],
        data=InsightData(**cached_data["data"]),
        cached=True,
        fetched_at=fetched_at
    )