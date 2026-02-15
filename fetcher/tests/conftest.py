"""Shared test fixtures and configuration for Service B tests."""
import pytest
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def test_settings():
    """Provide test configuration settings."""
    return {
        "coinmarketcap_base_url": "https://pro-api.coinmarketcap.com/v2",
        "coinmarketcap_api_key": "268531e0-7dd8-46ab-8b06-f54b78330408",
        "service_b_port": 8001,
        "log_level": "DEBUG"
    }


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch, test_settings):
    """Auto-use fixture to mock settings for all tests."""
    # Mock environment variables
    for key, value in test_settings.items():
        monkeypatch.setenv(key.upper(), str(value))


@pytest.fixture
def coinmarketcap_info_response_bitcoin():
    """
    Sample CoinMarketCap /v2/cryptocurrency/info API response for Bitcoin.
    Based on actual API structure.
    """
    return {
        "status": {
            "timestamp": "2026-02-15T10:30:00.000Z",
            "error_code": 0,
            "error_message": None,
            "elapsed": 10,
            "credit_count": 1
        },
        "data": {
            "bitcoin": {
                "id": 1,
                "name": "Bitcoin",
                "symbol": "BTC",
                "category": "coin",
                "description": "Bitcoin (BTC) is a cryptocurrency. Bitcoin is the original cryptocurrency.",
                "slug": "bitcoin",
                "logo": "https://s2.coinmarketcap.com/static/img/coins/64x64/1.png",
                "subreddit": "bitcoin",
                "notice": "",
                "tags": ["mineable", "pow", "sha-256"],
                "platform": None,
                "date_added": "2013-04-28T00:00:00.000Z",
                "twitter_username": "bitcoin",
                "is_hidden": 0,
                "date_launched": "2009-01-03T00:00:00.000Z",
                "contract_address": [],
                "self_reported_circulating_supply": 19500000,
                "self_reported_market_cap": 885000000000.0,
                "urls": {
                    "website": ["https://bitcoin.org/"],
                    "twitter": [],
                    "message_board": ["https://bitcointalk.org"],
                    "chat": [],
                    "facebook": [],
                    "explorer": ["https://blockchain.info/"],
                    "reddit": ["https://reddit.com/r/bitcoin"],
                    "technical_doc": ["https://bitcoin.org/bitcoin.pdf"],
                    "source_code": ["https://github.com/bitcoin/bitcoin"],
                    "announcement": []
                }
            }
        }
    }


@pytest.fixture
def coinmarketcap_info_response_with_platform():
    """Sample response for a token with platform information."""
    return {
        "status": {
            "timestamp": "2026-02-15T10:30:00.000Z",
            "error_code": 0,
            "error_message": None,
            "elapsed": 10,
            "credit_count": 1
        },
        "data": {
            "cardano": {
                "id": 2010,
                "name": "Cardano",
                "symbol": "ADA",
                "category": "coin",
                "description": "Cardano is a proof-of-stake blockchain platform.",
                "slug": "cardano",
                "logo": "https://s2.coinmarketcap.com/static/img/coins/64x64/2010.png",
                "platform": {
                    "id": 1027,
                    "name": "Ethereum",
                    "symbol": "ETH",
                    "slug": "ethereum",
                    "token_address": "0x..."
                },
                "date_launched": "2017-09-29T00:00:00.000Z",
                "self_reported_circulating_supply": 33000000000,
                "self_reported_market_cap": 16500000000.0
            }
        }
    }


@pytest.fixture
def empty_data_response():
    """Response with empty data."""
    return {
        "status": {
            "timestamp": "2026-02-15T10:30:00.000Z",
            "error_code": 0,
            "error_message": None
        },
        "data": {}
    }


@pytest.fixture
def missing_fields_response():
    """Response with missing required fields."""
    return {
        "status": {
            "timestamp": "2026-02-15T10:30:00.000Z",
            "error_code": 0,
            "error_message": None
        },
        "data": {
            "bitcoin": {
                "id": 1,
                "name": "Bitcoin",
                "symbol": "BTC",
                "category": "coin",
                "description": "Bitcoin description",
                "date_launched": "2009-01-03T00:00:00.000Z",
                "self_reported_circulating_supply": None,  # Missing required field
                "self_reported_market_cap": None  # Missing required field
            }
        }
    }
