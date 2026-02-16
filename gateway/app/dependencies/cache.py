import json
from typing import Optional

import redis
from redis.exceptions import RedisError

from app.config import settings
from app.models import InsightData

from app.dependencies.logger import logger

class RedisCache:
    """
    Redis-based cache with two-level key-value structure (Singleton).

    Structure:
    1. query_params -> request_id (maps query to unique request ID)
    2. request_id -> response_json (maps request ID to full response)

    Example:
    - Key: "query:symbol=BTC" -> Value: "req-uuid-123"
    - Key: "result:req-uuid-123" -> Value: {"symbol": 'bitcoin', ...}

    This class implements the Singleton pattern to ensure only one
    Redis connection is maintained throughout the application lifecycle.
    """

    _instance: Optional['RedisCache'] = None
    _initialized: bool = False


    def __new__(cls):
        """Ensure only one instance of RedisCache exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


    def __init__(self):
        """Initialize Redis connection (only once)."""
        # Only initialize once
        if RedisCache._initialized:
            return

        self._redis: Optional[redis.Redis] = None
        self._connect()
        RedisCache._initialized = True


    def _connect(self):
        """Establish Redis connection."""
        try:
            self._redis = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password if settings.redis_password else None,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self._redis.ping()
            logger.info(f"Redis connected: {settings.redis_host}:{settings.redis_port}")
        except RedisError as e:
            logger.error(f"Redis connection failed: {e}")
            self._redis = None


    def _get_query_key(self, query_params: str) -> str:
        """Generate key for query params -> request_id mapping."""
        return f"query:{query_params}"


    def _get_result_key(self, request_id: str) -> str:
        """Generate key for request_id -> result mapping."""
        return f"result:{request_id}"
    

    def get_by_request_id(self, request_id: str) -> Optional[dict]:
        """
        Get cached result directly by request ID.

        Args:
            request_id: Unique request identifier

        Returns:
            Result data dict if found, None otherwise
        """
        if not self._redis:
            logger.warning("Redis not available, cache miss")
            return None

        try:
            # Get result from request_id
            result_key = self._get_result_key(request_id)
            result_json = self._redis.get(result_key)

            if not result_json:
                logger.debug(f"Cache miss by request_id: {request_id}")
                return None

            # Parse JSON result
            result_data = json.loads(result_json)
            logger.info(f"Cache hit by request_id: {request_id}")
            return result_data  # Return the raw dict, not Pydantic objects

        except RedisError as e:
            logger.error(f"Redis error during get_by_request_id: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
    

    def get(self, query_params: str) -> Optional[tuple[dict, str]]:
        """
        Get cached result by query parameters.

        Args:
            query_params: Query parameters string (e.g., "symbol=BTC")

        Returns:
            Tuple of (result_data, request_id) if found, None otherwise
        """
        if not self._redis:
            logger.warning("Redis not available, cache miss")
            return None

        try:
            # Step 1: Get request_id from query params
            query_key = self._get_query_key(query_params)
            request_id = self._redis.get(query_key)

            if not request_id:
                logger.debug(f"Cache miss: {query_params}")
                return None

            # Step 2: Get result from request_id
            result_data = self.get_by_request_id(request_id)

            return (result_data, request_id)

        except RedisError as e:
            logger.error(f"Redis error during get: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
        
    
    def set(
        self,
        query_params: str,
        request_id: str,
        result_data: dict,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set cached result with two-level structure.

        Args:
            query_params: Query parameters string (e.g., "symbol=BTC")
            request_id: Unique request identifier
            result_data: Response data to cache
            ttl: Time-to-live in seconds (default from settings)

        Returns:
            True if successful, False otherwise
        """
        if not self._redis:
            logger.warning("Redis not available, cache set skipped")
            return False

        if ttl is None:
            ttl = settings.cache_ttl_seconds

        try:
            # Step 1: Store result_data with request_id
            result_key = self._get_result_key(request_id)
            result_json = json.dumps(result_data)
            self._redis.setex(result_key, ttl, result_json)

            # Step 2: Store query_params -> request_id mapping
            query_key = self._get_query_key(query_params)
            self._redis.setex(query_key, ttl, request_id)

            logger.info(
                f"Cache set: {query_params} -> {request_id} (TTL: {ttl}s)"
            )
            return True

        except RedisError as e:
            logger.error(f"Redis error during set: {e}")
            return False
        except (TypeError, ValueError) as e:
            logger.error(f"JSON encode error: {e}")
            return False
        

    def delete(self, query_params: str) -> bool:
        """
        Delete cached entry by query parameters.

        Args:
            query_params: Query parameters string

        Returns:
            True if deleted, False otherwise
        """
        if not self._redis:
            return False

        try:
            query_key = self._get_query_key(query_params)
            request_id = self._redis.get(query_key)

            if request_id:
                # Delete both keys
                result_key = self._get_result_key(request_id)
                self._redis.delete(query_key, result_key)
                logger.debug(f"Cache deleted: {query_params}")
                return True

            return False

        except RedisError as e:
            logger.error(f"Redis error during delete: {e}")
            return False
        

    def clear(self) -> int:
        """
        Clear all cache entries (query:* and result:* keys).

        Returns:
            Number of keys deleted
        """
        if not self._redis:
            return 0

        try:
            # Delete all query:* and result:* keys
            query_keys = list(self._redis.scan_iter("query:*"))
            result_keys = list(self._redis.scan_iter("result:*"))
            all_keys = query_keys + result_keys

            if all_keys:
                count = self._redis.delete(*all_keys)
                logger.info(f"Cache cleared: {count} keys removed")
                return count

            return 0

        except RedisError as e:
            logger.error(f"Redis error during clear: {e}")
            return 0


    def health_check(self) -> bool:
        """
        Check if Redis is available.

        Returns:
            True if Redis is responsive, False otherwise
        """
        if not self._redis:
            return False

        try:
            self._redis.ping()
            return True
        except RedisError:
            return False
        

        
# Global cache instance
cache = RedisCache()