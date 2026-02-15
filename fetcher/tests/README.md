# Service B Unit Tests

Comprehensive unit tests for Service B (External API Fetcher).

## Test Coverage

### Modules Tested

1. **`test_validators.py`** - Validator functions
   - `validate_symbol()` - Symbol validation and whitelist checking
   - `get_ticker_symbol()` - Symbol to ticker conversion
   - Edge cases: whitespace, case sensitivity, invalid symbols

2. **`test_coinmarketcap_client.py`** - CoinMarketCap API client
   - Client initialization
   - URL validation (SSRF protection)
   - Retry logic with exponential backoff
   - Data fetching and normalization
   - Error handling (400, 401, 404, 500, connection errors)
   - Response parsing and validation

3. **`test_routes_health.py`** - Health check endpoint
   - HTTP 200 response
   - Correct JSON structure
   - Timestamp validation
   - No authentication required
   - Content-type headers

4. **`test_routes_fetch.py`** - Cryptocurrency fetch endpoint
   - Valid/invalid symbol handling
   - Data structure validation
   - All allowed symbols
   - Case insensitivity
   - Error propagation
   - Client integration

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install -r requirements-test.txt
```

### Run All Tests

```bash
# From service_b directory
pytest
```

### Run Specific Test Files

```bash
# Run validator tests only
pytest tests/test_validators.py

# Run client tests only
pytest tests/test_coinmarketcap_client.py

# Run route tests only
pytest tests/test_routes_health.py tests/test_routes_fetch.py
```

### Run with Coverage

```bash
# Run tests with coverage report
pytest --cov=app --cov-report=html --cov-report=term

# View HTML coverage report
# Open htmlcov/index.html in browser
```

### Run Specific Test Classes or Methods

```bash
# Run specific test class
pytest tests/test_validators.py::TestValidateSymbol

# Run specific test method
pytest tests/test_validators.py::TestValidateSymbol::test_validate_symbol_valid_lowercase

# Run tests matching a pattern
pytest -k "validate_symbol"
```

### Verbose Output

```bash
# Show detailed test output
pytest -v

# Show print statements
pytest -s

# Both verbose and print statements
pytest -v -s
```

### Run Only Async Tests

```bash
pytest -m asyncio
```

## Test Structure

```
service_b/tests/
├── __init__.py                      # Package initializer
├── conftest.py                      # Shared fixtures and configuration
├── test_validators.py               # Validator function tests
├── test_coinmarketcap_client.py     # API client tests
├── test_routes_health.py            # Health endpoint tests
├── test_routes_fetch.py             # Fetch endpoint tests
└── README.md                        # This file
```

## Key Testing Patterns

### Mocking HTTP Calls

```python
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_fetch_data(client, mock_response):
    with patch('app.coinmarketcap_client.httpx.AsyncClient') as mock_client:
        # Setup mock
        mock_client.return_value.get.return_value = mock_response

        # Test
        result = await client.fetch_coin_data("bitcoin")

        # Assert
        assert result.symbol == "bitcoin"
```

### Testing FastAPI Endpoints

```python
from fastapi.testclient import TestClient

def test_endpoint(client):
    response = client.get("/v1/health")
    assert response.status_code == 200
```

### Testing Exception Handling

```python
def test_invalid_symbol_raises_error():
    with pytest.raises(HTTPException) as exc_info:
        validate_symbol("invalid")

    assert exc_info.value.status_code == 400
```

## Coverage Goals

- **Target Coverage**: 90%+ for all modules
- **Critical Paths**: 100% coverage for:
  - Validators (security-critical)
  - SSRF protection
  - Error handling paths
  - API response parsing

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```bash
# CI command example
pytest --cov=app --cov-report=xml --cov-report=term-missing --junitxml=junit.xml
```

## Troubleshooting

### Import Errors

If you get import errors, ensure you're running from the `service_b` directory:

```bash
cd service_b
pytest
```

### Async Test Errors

If async tests fail, ensure `pytest-asyncio` is installed:

```bash
pip install pytest-asyncio
```

### Mock Not Working

Ensure patches target the correct import path:

```python
# Patch where it's used, not where it's defined
with patch('app.routes.fetch.coinmarketcap_client.fetch_coin_data'):
    # Not: with patch('app.coinmarketcap_client.fetch_coin_data')
```

## Test Statistics

Total Tests: **60+**

Breakdown:
- Validators: 16 tests
- CoinMarketCap Client: 28 tests
- Health Route: 7 tests
- Fetch Route: 19 tests

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve coverage
4. Update this README if needed
