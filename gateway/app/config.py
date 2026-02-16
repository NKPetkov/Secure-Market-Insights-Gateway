import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(".env")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Authentication
    api_token: str = os.getenv("BEARER_TOKEN")
    
    # Service B connection
    fetcher_url: str = "http://localhost:8001"
    fetcher_timeout: int = 10
    
    # Cache configuration
    cache_ttl_seconds: int = 600  # 10 minutes
    
    # Rate limiting
    rate_limit_requests: int = 10
    rate_limit_window_seconds: int = 60  # 1 minute
    
    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_file_encoding="utf-8",
        extra="ignore"


# Global settings instance
settings = Settings()
