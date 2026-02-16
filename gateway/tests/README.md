# Service A Test Suite

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements-test.txt
```

### 2. Run All Tests
```bash
pytest
```

### 3. Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

### 4. View Coverage Report
```bash
# Open htmlcov/index.html in your browser
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_auth.py             # 20+ authentication tests
├── test_rate_limiter.py     # 13+ rate limiter tests
├── test_models.py           # 15+ model tests
├── test_routes_insights.py  # 15+ insights endpoint tests
└── test_routes_health.py    # Health endpoint tests
```

## Common Commands

```bash
# All tests
pytest

# Specific test file
pytest tests/test_auth.py

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run specific test
pytest tests/test_auth.py::TestValidateAuthorizationHeader::test_valid_token_success

# Run tests matching pattern
pytest -k auth
pytest -k "auth and not rate"
```

## Test Coverage

- **63+ test cases** total
- **Authentication, rate limiting, models, routes**
- **Target coverage:** >80% overall, >90% for critical modules

## Key Features

✅ Comprehensive authentication tests
✅ Rate limiter edge cases covered
✅ Pydantic model validation tests
✅ Full API endpoint tests
✅ Mocked external dependencies (Redis, Fetcher)
✅ Fast execution (no real external services)

## Documentation

For detailed testing documentation, see:
- `../TESTING.md` - Complete testing guide
- `../TEST_SUMMARY.md` - Test suite summary
- `../pytest.ini` - Pytest configuration

## Need Help?

Check the documentation or run:
```bash
pytest --help
```
