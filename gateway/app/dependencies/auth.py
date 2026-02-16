from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.dependencies.logger import logger

security = HTTPBearer(
    scheme_name="BearerAuth",
    description="Enter your Bearer token (without the 'Bearer' prefix)",
    auto_error=True
)


def _check_header_exists(authorization_header: str | None):
    # Check if header exists
    if not authorization_header:
        logger.warning("Missing Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
def _validate_header_scheme(authorization_header: str | None):
    parts = authorization_header.strip().split()

    if len(parts) != 2:
        logger.warning(f"Invalid Authorization header format: {authorization_header[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected: 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scheme, token = parts

    # Check Bearer scheme
    if scheme.lower().replace(":", "") != "bearer":
        logger.warning(f"Invalid authorization scheme: {scheme}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme. Expected: 'Bearer'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate token value
    if not token or len(token) == 0:
        logger.warning("Empty token in Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token


def validate_authorization_header(authorization_header: str | None) -> str:
    """
    Validate the Authorization header format and extract the token.

    Expected format: "Authorization: Bearer <token>"

    Args:
        authorization_header: The raw Authorization header value

    Returns:
        The validated token string

    Raises:
        HTTPException: If header is missing, malformed, or token is invalid
    """
    # Check if header exists
    _check_header_exists(authorization_header)

    # Validate format: "Bearer <token>"
    token = _validate_header_scheme(authorization_header)

    # Verify token matches configured token
    if token != settings.api_token:
        logger.warning(f"Invalid token attempt: {token[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug("Token validated successfully")
    return token