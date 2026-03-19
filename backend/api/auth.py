"""
Authentication API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from core.config import get_settings
from core.logging import get_logger
from core.cache import get_cache
from web3.auth_service import get_auth_service, AuthService
from web3.models import AuthMessageRequest, AuthVerifyRequest, AuthResponse
from api.models import RateLimitInfo

settings = get_settings()
logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/message", response_model=dict)
async def get_auth_message(request: AuthMessageRequest):
    """
    Get message to sign for authentication
    
    Send wallet address to receive a message that needs to be signed
    """
    try:
        auth_service = get_auth_service()
        message = await auth_service.generate_auth_message(request.address)
        
        return {
            "address": request.address,
            "message": message,
            "expires_in": settings.SIGNATURE_EXPIRATION_MINUTES * 60
        }
    except Exception as e:
        logger.error("Failed to generate auth message", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate message: {str(e)}"
        )


@router.post("/verify", response_model=AuthResponse)
async def verify_signature(request: AuthVerifyRequest):
    """
    Verify signature and get JWT tokens
    
    Send signed message to receive access and refresh tokens
    """
    try:
        auth_service = get_auth_service()
        
        tokens = await auth_service.verify_signature_and_issue_tokens(
            address=request.address,
            message=request.message,
            signature=request.signature
        )
        
        return AuthResponse(**tokens)
        
    except Exception as e:
        logger.error("Auth failed", address=request.address, error=str(e))
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_tokens(refresh_token: str):
    """
    Refresh access token using refresh token
    """
    try:
        auth_service = get_auth_service()
        
        tokens = await auth_service.refresh_tokens(refresh_token)
        
        return AuthResponse(**tokens)
        
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=401,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """
    Logout (blacklist current token)
    """
    if not authorization:
        raise HTTPException(status_code=400, detail="No token provided")
    
    # Extract token from "Bearer <token>"
    token = authorization
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    
    try:
        auth_service = get_auth_service()
        success = await auth_service.logout(token)
        
        return {"success": success, "message": "Logged out successfully"}
        
    except Exception as e:
        logger.error("Logout failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Logout failed: {str(e)}"
        )


@router.get("/rate-limit", response_model=RateLimitInfo)
async def get_rate_limit(
    authorization: Optional[str] = Header(None),
    x_forwarded_for: Optional[str] = Header(None)
):
    """
    Get current rate limit status
    """
    # Get identifier (address or IP)
    identifier = None
    if authorization:
        token = authorization.replace("Bearer ", "")
        cache = await get_cache()
        token_data = await cache.token_get(token)
        if token_data:
            identifier = token_data.get("address")
    
    if not identifier and x_forwarded_for:
        identifier = x_forwarded_for.split(",")[0].strip()
    
    if not identifier:
        identifier = "unknown"
    
    cache = await get_cache()
    
    # Check limits
    minute_key = f"rate:{identifier}:minute"
    hour_key = f"rate:{identifier}:hour"
    day_key = f"rate:{identifier}:day"
    
    minute_count = await cache.get(minute_key) or 0
    hour_count = await cache.get(hour_key) or 0
    day_count = await cache.get(day_key) or 0
    
    return RateLimitInfo(
        limit=settings.RATE_LIMIT_PER_MINUTE,
        remaining=max(0, settings.RATE_LIMIT_PER_MINUTE - minute_count),
        reset=60,
        limit_type="minute"
    )
