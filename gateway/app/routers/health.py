from datetime import datetime, timezone
from fastapi import APIRouter, status, Request
from app.models import HealthResponse

from app.dependencies.logger import logger
from app.dependencies.cache import cache
from app.dependencies.rate_limiter import rate_limit

app = APIRouter(prefix="/v1/health", tags=["Health"])


@app.get("/", response_model=HealthResponse, status_code=status.HTTP_200_OK)
@rate_limit()
def health_check(request: Request):
    """
    Health check endpoint.

    Returns:
        HealthResponse with current status and timestamp
    """
    # Check Redis health
    redis_healthy = cache.health_check()
    status_msg = "healthy" if redis_healthy else "degraded"

    if not redis_healthy:
        logger.warning("Health check: Redis not available")

    return HealthResponse(
        status=status_msg,
        timestamp=datetime.now(timezone.utc)
    )