from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.dependencies.logger import logger

security = HTTPBearer()


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> str:
    """
    Verify Bearer token from Authorization header.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        The validated token
        
    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    
    if token != settings.api_token:
        logger.warning(f"Invalid token attempt: {token[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.debug("Token validated successfully")
    return token