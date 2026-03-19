"""
JWT Token Manager
"""
import time
import jwt
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from core.config import get_settings
from core.logging import get_logger
from core.exceptions import (
    TokenExpiredException,
    TokenInvalidException,
    AuthException
)
from core.cache import get_cache

settings = get_settings()
logger = get_logger(__name__)


class TokenManager:
    """JWT token management"""
    
    def __init__(self):
        self.secret = settings.JWT_SECRET
        self.algorithm = settings.JWT_ALGORITHM
        self.expiration_minutes = settings.JWT_EXPIRATION_MINUTES
        self.refresh_expiration_days = settings.JWT_REFRESH_EXPIRATION_DAYS
    
    def create_token(
        self,
        address: str,
        token_type: str = "access"
    ) -> str:
        """
        Create JWT token
        
        Args:
            address: Wallet address
            token_type: "access" or "refresh"
        
        Returns:
            JWT token string
        """
        now = datetime.utcnow()
        
        if token_type == "access":
            exp = now + timedelta(minutes=self.expiration_minutes)
        else:
            exp = now + timedelta(days=self.refresh_expiration_days)
        
        payload = {
            "sub": address.lower(),
            "address": address,
            "type": token_type,
            "iat": now,
            "exp": exp,
            "jti": f"{address}-{time.time()}"
        }
        
        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        
        logger.info(
            f"Token created",
            address=address,
            type=token_type,
            expires=exp.isoformat()
        )
        
        return token
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and verify JWT token
        
        Args:
            token: JWT token string
        
        Returns:
            Decoded payload
        """
        try:
            # Check blacklist first
            cache = await get_cache()
            if await cache.token_blacklist_check(token):
                logger.warning("Token is blacklisted")
                raise TokenInvalidException()
            
            # Decode token
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm]
            )
            
            # Validate token type
            if payload.get("type") not in ("access", "refresh"):
                logger.warning("Invalid token type")
                raise TokenInvalidException()
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise TokenExpiredException()
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid token", error=str(e))
            raise TokenInvalidException()
    
    async def blacklist_token(self, token: str) -> bool:
        """Add token to blacklist"""
        try:
            cache = await get_cache()
            
            # Get expiration time
            try:
                payload = self.decode_token(token)
                exp = payload.get("exp", time.time() + 86400)
                ttl = int(exp - time.time())
                if ttl <= 0:
                    ttl = 86400
            except:
                ttl = 86400
            
            return await cache.token_blacklist_add(token, ttl=ttl)
            
        except Exception as e:
            logger.error("Failed to blacklist token", error=str(e))
            return False
    
    def refresh_token(self, refresh_token: str) -> str:
        """
        Create new access token from refresh token
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            New access token
        """
        payload = self.decode_token(refresh_token)
        
        if payload.get("type") != "refresh":
            logger.warning("Cannot refresh with access token")
            raise AuthException("Invalid refresh token")
        
        address = payload.get("address")
        return self.create_token(address, token_type="access")
    
    def get_token_info(self, token: str) -> Dict[str, Any]:
        """Get token information without full validation"""
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )
            
            return {
                "address": payload.get("address"),
                "type": payload.get("type"),
                "issued_at": payload.get("iat"),
                "expires": payload.get("exp"),
                "is_expired": payload.get("exp", 0) < time.time()
            }
        except:
            return {}


# Global token manager instance
token_manager = TokenManager()


def get_token_manager() -> TokenManager:
    """Get token manager dependency"""
    return token_manager
