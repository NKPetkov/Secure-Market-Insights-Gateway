from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class CryptoInsightOutput(BaseModel):
    """Normalized cryptocurrency insight output data."""

    symbol: str                         = Field(..., description="Cryptocurrency symbol (e.g., bitcoin)")
    name: str                           = Field(..., description="Cryptocurrency name")
    category: str                       = Field(..., description="Cryptocurrency category, eg. coin, token")
    description: str                    = Field(..., description="Cryptocurrency description")
    date_launched: Optional[str]        = Field(None, description="Launch date of hte cryptocurrency")
    logo: Optional[str]                 = Field(None, description="Cryptocurrency logo")
    platform: Optional[str]             = Field(None, description="Name of the platform hosting the cryptocurrency")
    circulating_suply: Optional[float]  = Field(None, description="Suply of the cryptocurrency in circulation")
    market_cap: Optional[float]         = Field(None, description="Cryptocurrency market cap")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: datetime
