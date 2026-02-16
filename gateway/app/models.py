from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class InsightRequest(BaseModel):
    """Request model for creating an insight."""

    symbol: str = Field(..., description="Cryptocurrency symbol (e.g., BTC, ETH)")


class InsightData(BaseModel):
    """Normalized insight data from outside API (eg. fetcher service)"""

    symbol: str                         = Field(..., description="Cryptocurrency symbol (e.g., bitcoin)")
    name: str                           = Field(..., description="Cryptocurrency name")
    category: str                       = Field(..., description="Cryptocurrency category, eg. coin, token")
    description: str                    = Field(..., description="Cryptocurrency description")
    date_launched: Optional[str]        = Field(None, description="Launch date of the cryptocurrency")
    logo: Optional[str]                 = Field(None, description="Cryptocurrency logo")
    platform: Optional[str]             = Field(None, description="Name of the platform hosting the cryptocurrency")
    circulating_suply: Optional[float]  = Field(None, description="Suply of the cryptocurrency in circulation")
    market_cap: Optional[float]         = Field(None, description="Cryptocurrency market cap")


class InsightResponse(BaseModel):
    """Response model for insight requests."""

    request_id: str = Field(..., description="Unique request identifier")
    symbol: str = Field(..., description="Requested symbol")
    data: InsightData = Field(..., description="Market insights data")
    cached: bool = Field(..., description="Whether data was served from cache")
    fetched_at: datetime = Field(..., description="When data was fetched")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: datetime