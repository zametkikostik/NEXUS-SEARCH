"""
Web3 Models
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from eth_utils import is_address


class AuthMessageRequest(BaseModel):
    """Request for auth message"""
    address: str = Field(..., description="Wallet address")
    
    @field_validator('address')
    @classmethod
    def validate_address(cls, v):
        if not is_address(v):
            raise ValueError("Invalid Ethereum address format")
        return v


class AuthVerifyRequest(BaseModel):
    """Request for signature verification"""
    address: str = Field(..., description="Wallet address")
    signature: str = Field(..., description="Signature")
    message: str = Field(..., description="Original message")
    
    @field_validator('address')
    @classmethod
    def validate_address(cls, v):
        if not is_address(v):
            raise ValueError("Invalid Ethereum address format")
        return v
    
    @field_validator('signature')
    @classmethod
    def validate_signature(cls, v):
        if not v.startswith('0x'):
            return '0x' + v
        return v


class AuthResponse(BaseModel):
    """Auth response"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = "Bearer"
    expires_in: int = Field(..., description="Token expiration in seconds")
    address: str = Field(..., description="Wallet address")


class TokenBalanceRequest(BaseModel):
    """Token balance request"""
    address: str = Field(..., description="Wallet address")


class TokenBalanceResponse(BaseModel):
    """Token balance response"""
    address: str
    balance: str = Field(..., description="Token balance (wei)")
    balance_formatted: float = Field(..., description="Token balance (formatted)")
    symbol: str = "NXS"
    decimals: int = 18


class PaymentRequest(BaseModel):
    """Payment request for search"""
    address: str
    amount: float
    signature: str
