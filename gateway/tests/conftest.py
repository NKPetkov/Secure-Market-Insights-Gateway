"""Shared test fixtures and configuration for Service A tests."""
import pytest
import os
import sys
from unittest.mock import patch
import fakeredis

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def test_settings():
    """Provide test configuration settings."""
    return {
        "api_token": "test-token-12345",
        "fetcher_url": "http://localhost:8000",
        "fetcher_timeout": 10,
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": "0",
        "redis_password": "",
        "cache_ttl_seconds": 600,
        "rate_limit_requests": 10,
        "rate_limit_window_seconds": 60,
        "log_level": "DEBUG"
    }


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch, test_settings):
    """Auto-use fixture to mock settings for all tests."""
    # Mock environment variables first
    for key, value in test_settings.items():
        monkeypatch.setenv(key.upper(), str(value))

    # Directly patch the settings object attributes
    from app.config import settings
    for key, value in test_settings.items():
        monkeypatch.setattr(settings, key, value)


@pytest.fixture
def valid_token(test_settings):
    """Return the valid API token from test settings."""
    return test_settings["api_token"]


@pytest.fixture
def auth_headers(valid_token):
    """Return valid authorization headers."""
    return {"Authorization": f"Bearer {valid_token}"}


@pytest.fixture
def mock_redis():
    """Create a fake Redis instance for testing."""
    fake_redis = fakeredis.FakeRedis(decode_responses=True)
    return fake_redis


@pytest.fixture
def mock_cache(mock_redis):
    """Mock the cache to use fake Redis."""
    with patch('app.dependencies.cache.cache._redis', mock_redis):
        yield


@pytest.fixture
def fetcher_success_response_bitcoin():
    """
    Sample successful fetcher service response for Bitcoin.
    Matches the structure expected by Service A.
    """
    return {
        "symbol": "bitcoin",
        "name": "Bitcoin",
        "category": "coin",
        "description": "Bitcoin (BTC) is a cryptocurrency. Bitcoin is the original cryptocurrency.",
        "date_launched": "2009-01-03T00:00:00.000Z",
        "logo": "https://s2.coinmarketcap.com/static/img/coins/64x64/1.png",
        "platform": None,
        "circulating_suply": 19500000.0,
        "market_cap": 885000000000.0
    }


@pytest.fixture
def fetcher_success_response_with_platform():
    """Sample response for a token with platform information."""
    return {
        "symbol": "cardano",
        "name": "Cardano",
        "category": "coin",
        "description": "Cardano is a proof-of-stake blockchain platform.",
        "date_launched": "2017-09-29T00:00:00.000Z",
        "logo": "https://s2.coinmarketcap.com/static/img/coins/64x64/2010.png",
        "platform": "Ethereum",
        "circulating_suply": 33000000000.0,
        "market_cap": 16500000000.0
    }


@pytest.fixture
def mock_fetcher_success(fetcher_success_response_bitcoin):
    """Mock successful fetcher service response."""
    # Patch where it's used (in insights router), not where it's defined
    with patch('app.routers.insights.fetch_symbol_data', return_value=fetcher_success_response_bitcoin):
        yield fetcher_success_response_bitcoin


@pytest.fixture
def mock_fetcher_failure():
    """Mock failed fetcher service response."""
    from fastapi import HTTPException

    def raise_error(*args, **kwargs):
        raise HTTPException(status_code=503, detail="Fetcher service unavailable")

    # Patch where it's used (in insights router), not where it's defined
    with patch('app.routers.insights.fetch_symbol_data', side_effect=raise_error):
        yield


@pytest.fixture
def clear_rate_limiter():
    """Clear rate limiter state before each test."""
    from app.dependencies.rate_limiter import _rate_limiter
    _rate_limiter._requests.clear()
    yield
    _rate_limiter._requests.clear()


@pytest.fixture(autouse=True)
def reset_test_state(clear_rate_limiter):
    """Automatically reset state before each test."""
    pass
