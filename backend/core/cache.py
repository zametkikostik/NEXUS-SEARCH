"""
Redis Cache Client
"""
import json
import redis.asyncio as redis
from typing import Any, Optional, List
from core.config import get_settings
from core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class CacheClient:
    """Async Redis cache client"""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self._connected = False
    
    async def connect(self) -> None:
        """Connect to Redis"""
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            await self.client.ping()
            self._connected = True
            logger.info("Connected to Redis", host=settings.REDIS_HOST, port=settings.REDIS_PORT)
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            self._connected = False
    
    async def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
            self._connected = False
            logger.info("Disconnected from Redis")
    
    @property
    def is_connected(self) -> bool:
        """Check if connected"""
        return self._connected
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self._connected:
            return None
        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error("Cache get error", key=key, error=str(e))
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache"""
        if not self._connected:
            return False
        try:
            serialized = json.dumps(value)
            if ttl is None:
                ttl = settings.CACHE_TTL_DEFAULT
            await self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error("Cache set error", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self._connected:
            return False
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error("Cache delete error", key=key, error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self._connected:
            return False
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error("Cache exists error", key=key, error=str(e))
            return False
    
    async def get_ttl(self, key: str) -> int:
        """Get TTL for key"""
        if not self._connected:
            return -1
        try:
            return await self.client.ttl(key)
        except Exception as e:
            logger.error("Cache TTL error", key=key, error=str(e))
            return -1
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter"""
        if not self._connected:
            return None
        try:
            return await self.client.incr(key, amount)
        except Exception as e:
            logger.error("Cache increment error", key=key, error=str(e))
            return None
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration on key"""
        if not self._connected:
            return False
        try:
            return await self.client.expire(key, ttl)
        except Exception as e:
            logger.error("Cache expire error", key=key, error=str(e))
            return False
    
    async def get_rate_limit(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """
        Check rate limit using sliding window
        Returns: (allowed, remaining)
        """
        if not self._connected:
            return True, limit
        
        try:
            current_time = int(time.time())
            window_key = f"rate:{key}:{current_time // window}"
            
            count = await self.client.get(window_key)
            count = int(count) if count else 0
            
            if count >= limit:
                return False, 0
            
            pipe = self.client.pipeline()
            pipe.incr(window_key)
            pipe.expire(window_key, window * 2)
            await pipe.execute()
            
            remaining = max(0, limit - count - 1)
            return True, remaining
        except Exception as e:
            logger.error("Rate limit error", key=key, error=str(e))
            return True, limit
    
    async def search_cache_get(self, query_hash: str) -> Optional[List[dict]]:
        """Get search results from cache"""
        key = f"search:{query_hash}"
        return await self.get(key)
    
    async def search_cache_set(
        self,
        query_hash: str,
        results: List[dict],
        is_news: bool = False
    ) -> bool:
        """Save search results to cache"""
        key = f"search:{query_hash}"
        ttl = settings.CACHE_TTL_NEWS if is_news else settings.CACHE_TTL_DEFAULT
        return await self.set(key, results, ttl=ttl)
    
    async def auth_message_get(self, address: str) -> Optional[str]:
        """Get auth message for wallet"""
        key = f"auth:message:{address.lower()}"
        return await self.get(key)
    
    async def auth_message_set(self, address: str, message: str, ttl: int = 600) -> bool:
        """Save auth message for wallet"""
        key = f"auth:message:{address.lower()}"
        return await self.set(key, message, ttl=ttl)
    
    async def token_get(self, token: str) -> Optional[dict]:
        """Get JWT token data"""
        key = f"token:{token}"
        return await self.get(key)
    
    async def token_set(self, token: str, data: dict, ttl: int = 3600) -> bool:
        """Save JWT token data"""
        key = f"token:{token}"
        return await self.set(key, data, ttl=ttl)
    
    async def token_blacklist_add(self, token: str, ttl: int = 86400) -> bool:
        """Add token to blacklist"""
        key = f"token:blacklist:{token}"
        return await self.set(key, "1", ttl=ttl)
    
    async def token_blacklist_check(self, token: str) -> bool:
        """Check if token is blacklisted"""
        key = f"token:blacklist:{token}"
        return await self.exists(key)


# Global cache instance
cache = CacheClient()


async def get_cache() -> CacheClient:
    """Get cache client dependency"""
    if not cache.is_connected:
        await cache.connect()
    return cache
