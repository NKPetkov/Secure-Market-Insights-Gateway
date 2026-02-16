from datetime import datetime, timezone
from fastapi import APIRouter, status
from ..models import HealthResponse

app = APIRouter(prefix="/v1/health", tags=["health"])


@app.get("/", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def health_check():
    """
    Health check endpoint.

    Returns:
        HealthResponse with current status and timestamp
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc)
    )