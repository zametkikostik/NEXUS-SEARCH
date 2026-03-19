"""
Web3 Authentication Service
"""
import time
from typing import Optional, Dict, Any
from core.config import get_settings
from core.logging import get_logger
from core.cache import get_cache
from core.exceptions import AuthException, SignatureExpiredException
from web3.signature import SignatureVerifier, get_signature_verifier
from web3.jwt_manager import TokenManager, get_token_manager

settings = get_settings()
logger = get_logger(__name__)


class AuthService:
    """Web3 authentication service"""
    
    def __init__(self):
        self.verifier: Optional[SignatureVerifier] = None
        self.token_manager: Optional[TokenManager] = None
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize service"""
        if self._initialized:
            return
        
        self.verifier = get_signature_verifier()
        self.token_manager = get_token_manager()
        self._initialized = True
        logger.info("Auth service initialized")
    
    async def generate_auth_message(
        self,
        address: str
    ) -> str:
        """
        Generate message for wallet signature
        
        Args:
            address: Wallet address
        
        Returns:
            Message to sign
        """
        if not self._initialized:
            self.initialize()
        
        # Generate nonce for replay protection
        nonce = f"{address}-{time.time()}"
        message = self.verifier.generate_message(address, nonce)
        
        # Cache message for verification
        cache = await get_cache()
        await cache.auth_message_set(address, message, ttl=600)
        
        logger.info("Auth message generated", address=address)
        return message
    
    async def verify_signature_and_issue_tokens(
        self,
        address: str,
        message: str,
        signature: str
    ) -> Dict[str, Any]:
        """
        Verify signature and issue JWT tokens
        
        Args:
            address: Wallet address
            message: Signed message
            signature: Signature
        
        Returns:
            Dict with access_token, refresh_token, expires_in, address
        """
        if not self._initialized:
            self.initialize()
        
        # Check if message is expired
        if self.verifier.is_message_expired(message):
            logger.warning("Message expired", address=address)
            raise SignatureExpiredException()
        
        # Verify signature
        is_valid, recovered_address = self.verifier.verify_signature(
            address, message, signature
        )
        
        if not is_valid:
            raise AuthException("Signature verification failed")
        
        # Issue tokens
        access_token = self.token_manager.create_token(address, token_type="access")
        refresh_token = self.token_manager.create_token(address, token_type="refresh")
        
        # Cache token data
        cache = await get_cache()
        await cache.token_set(
            access_token,
            {"address": address, "type": "access"},
            ttl=settings.JWT_EXPIRATION_MINUTES * 60
        )
        
        logger.info(
            "Auth successful",
            address=address,
            access_token=access_token[:20] + "..."
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": settings.JWT_EXPIRATION_MINUTES * 60,
            "address": address
        }
    
    async def refresh_tokens(
        self,
        refresh_token: str
    ) -> Dict[str, Any]:
        """
        Refresh access token
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            New token pair
        """
        if not self._initialized:
            self.initialize()
        
        # Verify refresh token
        payload = self.token_manager.decode_token(refresh_token)
        address = payload.get("address")
        
        # Issue new tokens
        new_access_token = self.token_manager.create_token(address, token_type="access")
        new_refresh_token = self.token_manager.create_token(address, token_type="refresh")
        
        # Blacklist old refresh token
        await self.token_manager.blacklist_token(refresh_token)
        
        logger.info("Tokens refreshed", address=address)
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "Bearer",
            "expires_in": settings.JWT_EXPIRATION_MINUTES * 60,
            "address": address
        }
    
    async def logout(self, access_token: str) -> bool:
        """
        Logout (blacklist token)
        
        Args:
            access_token: Access token to blacklist
        
        Returns:
            Success status
        """
        if not self._initialized:
            self.initialize()
        
        return await self.token_manager.blacklist_token(access_token)
    
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate access token
        
        Args:
            token: JWT token
        
        Returns:
            Token payload or None
        """
        if not self._initialized:
            self.initialize()
        
        try:
            payload = self.token_manager.decode_token(token)
            return payload
        except:
            return None


# Global auth service instance
auth_service = AuthService()


def get_auth_service() -> AuthService:
    """Get auth service dependency"""
    if not auth_service._initialized:
        auth_service.initialize()
    return auth_service
