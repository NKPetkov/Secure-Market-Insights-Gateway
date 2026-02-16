from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuration settings"""

    coinmarketcap_base_url: str = "https://pro-api.coinmarketcap.com/v2"
    coinmarketcap_api_key: str = "dev-token-change-in-production"
    fetcher_port: int = 8001
    log_level: str = "INFO"
    outside_request_timeout: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_file_encoding="utf-8",
        extra="ignore"


settings = Settings()