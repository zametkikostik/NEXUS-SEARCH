"""
Custom Exceptions
"""
from typing import Optional, Any, Dict


class NexusException(Exception):
    """Base exception for Nexus Search"""
    
    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details
        }


class SearchException(NexusException):
    """Search-related errors"""
    
    def __init__(
        self,
        message: str = "Search failed",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code, details)


class ProviderException(NexusException):
    """Provider-related errors"""
    
    def __init__(
        self,
        provider: str,
        message: str = "Provider error",
        status_code: int = 502,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details["provider"] = provider
        super().__init__(message, status_code, details)
        self.provider = provider


class ProviderTimeoutException(ProviderException):
    """Provider timeout"""
    
    def __init__(self, provider: str, timeout: int = 10):
        super().__init__(
            provider=provider,
            message=f"Provider {provider} timed out after {timeout}s",
            status_code=504
        )


class ProviderBanException(ProviderException):
    """Provider ban detected"""
    
    def __init__(self, provider: str):
        super().__init__(
            provider=provider,
            message=f"IP banned by {provider}",
            status_code=403
        )


class ContentFilterException(NexusException):
    """Content filtered out"""
    
    def __init__(
        self,
        reason: str = "content_blocked",
        category: Optional[str] = None
    ):
        details = {"reason": reason}
        if category:
            details["category"] = category
        super().__init__(
            message="Content was filtered out",
            status_code=403,
            details=details
        )


class AuthException(NexusException):
    """Authentication errors"""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        status_code: int = 401,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code, details)


class SignatureExpiredException(AuthException):
    """Signature expired"""
    
    def __init__(self):
        super().__init__(
            message="Signature has expired",
            status_code=401,
            details={"reason": "signature_expired"}
        )


class SignatureInvalidException(AuthException):
    """Invalid signature"""
    
    def __init__(self):
        super().__init__(
            message="Invalid signature",
            status_code=401,
            details={"reason": "invalid_signature"}
        )


class TokenExpiredException(AuthException):
    """JWT token expired"""
    
    def __init__(self):
        super().__init__(
            message="Token has expired",
            status_code=401,
            details={"reason": "token_expired"}
        )


class TokenInvalidException(AuthException):
    """Invalid JWT token"""
    
    def __init__(self):
        super().__init__(
            message="Invalid token",
            status_code=401,
            details={"reason": "invalid_token"}
        )


class RateLimitException(NexusException):
    """Rate limit exceeded"""
    
    def __init__(
        self,
        retry_after: int = 60,
        limit_type: str = "minute"
    ):
        super().__init__(
            message="Rate limit exceeded",
            status_code=429,
            details={
                "retry_after": retry_after,
                "limit_type": limit_type
            }
        )


class IPFSException(NexusException):
    """IPFS-related errors"""
    
    def __init__(
        self,
        message: str = "IPFS operation failed",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code, details)


class IPFSUploadException(IPFSException):
    """IPFS upload failed"""
    
    def __init__(self, message: str = "Failed to upload to IPFS"):
        super().__init__(message=message, status_code=500)


class IPFSDownloadException(IPFSException):
    """IPFS download failed"""
    
    def __init__(self, cid: str):
        super().__init__(
            message=f"Failed to download from IPFS: {cid}",
            status_code=404,
            details={"cid": cid}
        )


class CircuitBreakerOpenException(NexusException):
    """Circuit breaker is open"""
    
    def __init__(self, provider: str, retry_after: int = 60):
        super().__init__(
            message=f"Circuit breaker open for {provider}",
            status_code=503,
            details={
                "provider": provider,
                "retry_after": retry_after
            }
        )


class ProxyException(NexusException):
    """Proxy-related errors"""
    
    def __init__(
        self,
        message: str = "Proxy error",
        status_code: int = 502,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code, details)


class NoAvailableProxiesException(ProxyException):
    """No proxies available"""
    
    def __init__(self):
        super().__init__(
            message="No available proxies",
            status_code=503
        )


class PaymentException(NexusException):
    """Payment-related errors"""
    
    def __init__(
        self,
        message: str = "Payment failed",
        status_code: int = 402,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code, details)


class InsufficientBalanceException(PaymentException):
    """Insufficient token balance"""
    
    def __init__(self, required: float, balance: float):
        super().__init__(
            message="Insufficient token balance",
            status_code=402,
            details={
                "required": required,
                "balance": balance
            }
        )
