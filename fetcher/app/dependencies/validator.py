"""Input validation for Service B."""
from fastapi import HTTPException, status

# Whitelist of allowed cryptocurrency symbols
ALLOWED_SYMBOLS = {
    "bitcoin": 1,
    "ethereum": 1027,
    "cardano": 2010,
    "solana": 5426
}


def validate_symbol(symbol: str) -> str:
    """
    Validate that the symbol is in the allowed whitelist.

    Args:
        symbol: Cryptocurrency symbol to validate

    Returns:
        Validated symbol in lowercase

    Raises:
        HTTPException: If symbol is not in whitelist
    """
    symbol_lower = symbol.lower().strip()

    if symbol_lower not in ALLOWED_SYMBOLS.keys():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid symbol. Allowed symbols: {', '.join(ALLOWED_SYMBOLS.keys())}"
        )

    return symbol_lower
