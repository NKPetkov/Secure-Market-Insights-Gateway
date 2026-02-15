# Testing Quick Start Guide

## Setup (One Time)

```bash
# Navigate to service_b directory
cd service_b

# Install test dependencies
pip install -r requirements-test.txt
```

## Run Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app

# Run with HTML coverage report
pytest --cov=app --cov-report=html
# Then open: htmlcov/index.html
```

### Run Specific Tests

```bash
# Single file
pytest tests/test_validators.py

# Single class
pytest tests/test_validators.py::TestValidateSymbol

# Single test
pytest tests/test_validators.py::TestValidateSymbol::test_validate_symbol_valid_lowercase

# Pattern matching
pytest -k "validate_symbol"
pytest -k "health"
pytest -k "fetch"
```

### Useful Options

```bash
# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Quiet output (less verbose)
pytest -q

# Run last failed tests only
pytest --lf

# Show slowest 10 tests
pytest --durations=10
```

## Test Files

| File | Tests | What It Tests |
|------|-------|---------------|
| `test_validators.py` | 16 | Input validation & symbol conversion |
| `test_coinmarketcap_client.py` | 28 | API client, SSRF, retries, errors |
| `test_routes_health.py` | 7 | Health check endpoint |
| `test_routes_fetch.py` | 19 | Fetch endpoint & integration |
| `test_models.py` | 20 | Pydantic models |

## Expected Output

```
============================= test session starts ==============================
collected 90 items

tests/test_validators.py ................                                 [ 17%]
tests/test_coinmarketcap_client.py ............................           [ 48%]
tests/test_routes_health.py .......                                       [ 56%]
tests/test_routes_fetch.py ...................                            [ 77%]
tests/test_models.py ....................                                 [100%]

============================== 90 passed in 2.45s ==============================
```

## Coverage Report

```bash
pytest --cov=app --cov-report=term-missing
```

Shows:
- Which lines are covered
- Which lines are missing coverage
- Overall percentage

## Troubleshooting

### Import Errors
```bash
# Ensure you're in the service_b directory
cd service_b
pytest
```

### Async Test Errors
```bash
# Install pytest-asyncio
pip install pytest-asyncio
```

### Mock Not Working
Check the import path in the patch decorator:
```python
# Correct - patch where it's used
with patch('app.routes.fetch.coinmarketcap_client'):

# Wrong - patching where it's defined
with patch('app.coinmarketcap_client'):
```

## CI/CD Command

```bash
# For continuous integration
pytest --cov=app --cov-report=xml --cov-report=term --junitxml=junit.xml
```

## Quick Test Examples

### Test a Validator
```bash
pytest tests/test_validators.py::TestValidateSymbol::test_validate_symbol_valid_lowercase -v
```

### Test SSRF Protection
```bash
pytest tests/test_coinmarketcap_client.py::TestValidateUrl -v
```

### Test Health Endpoint
```bash
pytest tests/test_routes_health.py -v
```

### Test All Routes
```bash
pytest tests/test_routes_*.py -v
```

## Test Statistics

- **Total Tests**: 90
- **Target Coverage**: 90%+
- **Expected Runtime**: ~2-3 seconds

## Next Steps

1. Run `pytest` to see all tests pass
2. Run `pytest --cov=app --cov-report=html` to see coverage
3. Open `htmlcov/index.html` in browser
4. Check which modules have 100% coverage

## Documentation

- Full test details: `tests/README.md`
- Test summary: `TEST_SUMMARY.md`
- This quick start: `TESTING_QUICK_START.md`
