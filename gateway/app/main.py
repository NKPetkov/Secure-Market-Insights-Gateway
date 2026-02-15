from fastapi import FastAPI
from fastapi.responses import JSONResponse

from contextlib import asynccontextmanager

from .routers import health, fetch
from .dependencies.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Fetcher service starting up...")
    yield
    logger.info("Fetcher service shutting down...")

app = FastAPI(
    title="Fetcher service - External API Fetcher",
    description="Fetches cryptocurrency data from CoinMarketCap API",
    version="1.0.0",
    lifespan=lifespan
)

### ROUTING ###
app.include_router(health.app)
app.include_router(fetch.app)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unexpected errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )