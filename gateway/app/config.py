from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Authentication
    api_token: str = "dev-token-change-in-production"
    
    # Service B connection
    fetcher_url: str        = "http://localhost:8000"
    fetcher_timeout: int    = 10
    
    # Cache configuration
    cache_ttl_seconds: int = 600  # 10 minutes
    
    # Rate limiting
    rate_limit_requests: int        = 10
    rate_limit_window_seconds: int  = 60  # 1 minute

    # Redis
    redis_host: str     = "localhost"
    redis_port: int     = 5665
    redis_db: str       = "0"
    redis_password: str = ""
    
    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_file_encoding="utf-8",
        extra="ignore"


# Global settings instance
settings = Settings()