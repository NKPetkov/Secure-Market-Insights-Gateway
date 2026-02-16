import time
from collections import defaultdict
from functools import wraps
from typing import Callable, Dict

from fastapi import HTTPException, status, Request

from app.config import settings
from app.dependencies.logger import logger


class TokenRateLimiter:
    """In-memory rate limiter using sliding window, keyed by bearer token."""

    def __init__(self):
        # Store: {token: [timestamp1, timestamp2, ...]}
        self._requests: Dict[str, list[float]] = defaultdict(list)

    def _clean_old_requests(self, token: str, window_start: float):
        """Remove requests outside the current window."""
        self._requests[token] = [
            ts for ts in self._requests[token] if ts > window_start
        ]

    def check_limit(self, token: str, rate_limit: int | None = None, time_limit: int | None = None) -> None:
        """
        Check if request is within rate limit for the given token.

        Args:
            token: Bearer token

        Raises:
            HTTPException: If rate limit is exceeded
        """
        current_time = time.time()

        # Use token hash for logging (privacy)
        token_id = f"token:{hash(token) % 10000:04d}"

        time_limit = time_limit or settings.rate_limit_window_seconds

        # Clean old requests
        self._clean_old_requests(token, current_time - time_limit)

        # Check limit
        request_count = len(self._requests[token])

        rate_limit = rate_limit or settings.rate_limit_requests

        if request_count >= rate_limit:
            logger.warning(
                f"Rate limit exceeded for {token_id}: "
                f"{request_count}/{rate_limit} requests"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {rate_limit} "
                       f"requests per {time_limit} seconds.",
                headers={"Retry-After": str(time_limit)}
            )

        # Add current request
        self._requests[token].append(current_time)
        logger.debug(
            f"Rate limit check passed for {token_id}: "
            f"{request_count + 1}/{rate_limit}"
        )

# Global rate limiter instance
_rate_limiter = TokenRateLimiter()


def rate_limit(max_calls: int | None = None, time_frame: int | None = None):
    def decorator(func: Callable) -> Callable:
        """
        Decorator to enforce rate limiting on endpoints based on bearer token.

        The decorated function must have a 'token' parameter that contains
        the validated bearer token (typically from the verify_token dependency).

        Usage:
            @app.post("/endpoint")
            @rate_limit
            async def my_endpoint(token: str = Depends(verify_token)):
                ...
        """
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Extract token from kwargs (injected by verify_token dependency)
            token = kwargs.get('token')

            if not token:
                logger.error("Rate limiter decorator used on endpoint without token parameter")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Rate limiting configuration error"
                )

            # Check rate limit
            _rate_limiter.check_limit(token, max_calls, time_frame)

            # Call the original function
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator