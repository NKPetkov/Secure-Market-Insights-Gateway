import uuid
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse

from app.config import settings

from app.dependencies.logger import logger
from app.dependencies.cache import cache

from app.routers import (
    health,
    insights
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Service A (API Gateway) starting up...")
    logger.info(f"Service B URL: {settings.fetcher_url}")
    logger.info(f"Redis: {settings.redis_host}:{settings.redis_port}")
    logger.info(f"Cache TTL: {settings.cache_ttl_seconds}s")
    logger.info(f"Rate limit: {settings.rate_limit_requests} requests per {settings.rate_limit_window_seconds}s")

    # Check Redis connection
    if cache.health_check():
        logger.info("Redis connected successfully")
    else:
        logger.warning("Redis connection failed - caching will be disabled")

    yield
    logger.info("Service A shutting down...")
    cache.clear()


########## INTI FASTAPI ##########
app = FastAPI(
    title="Secure Market Insights Gateway - Service A",
    description="API Gateway for cryptocurrency market insights",
    version="1.0.0",
    lifespan=lifespan
)
##################################

# ROUTERS
app.include_router(health.app)
app.include_router(insights.app)
######


# ERROR HANDLERS
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom exception handler for HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Custom exception handler for general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )
####