#!/bin/bash
# Script to run all Service B tests with coverage

echo "========================================="
echo "Running Service B Unit Tests"
echo "========================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "Error: pytest is not installed"
    echo "Please run: pip install -r requirements-test.txt"
    exit 1
fi

# Run tests with coverage
echo "Running tests with coverage..."
pytest tests/ \
    --cov=app \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-report=xml \
    -v \
    --tb=short

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✓ All tests passed!"
    echo "========================================="
    echo ""
    echo "Coverage report generated:"
    echo "  - HTML: htmlcov/index.html"
    echo "  - XML: coverage.xml"
    echo ""
else
    echo ""
    echo "========================================="
    echo "✗ Some tests failed"
    echo "========================================="
    echo ""
    exit 1
fi
