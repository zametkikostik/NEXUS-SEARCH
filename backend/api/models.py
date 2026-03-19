"""
API Models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class SearchRequest(BaseModel):
    """Search request"""
    q: str = Field(..., description="Search query", min_length=1, max_length=500)
    providers: Optional[List[str]] = Field(default=None, description="Provider names")
    limit: int = Field(default=10, ge=1, le=50, description="Max results")
    timeout: Optional[float] = Field(default=None, description="Timeout in seconds")
    cache: bool = Field(default=True, description="Use cache")
    filter_content: bool = Field(default=True, description="Filter inappropriate content")
    store_ipfs: bool = Field(default=False, description="Store results in IPFS")


class SearchResponse(BaseModel):
    """Search response"""
    query: str
    results: List[Dict[str, Any]]
    total: int
    providers_used: List[str]
    time_ms: float
    cached: bool = False
    ipfs_cid: Optional[str] = None


class HealthStatus(str, Enum):
    """Health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthResponse(BaseModel):
    """Health check response"""
    status: HealthStatus
    version: str = "1.0.0"
    timestamp: float
    services: Dict[str, bool] = Field(default_factory=dict)


class ProviderStatus(BaseModel):
    """Provider status"""
    name: str
    enabled: bool
    healthy: bool
    latency_ms: Optional[float] = None
    success_rate: Optional[float] = None


class ProvidersResponse(BaseModel):
    """Providers status response"""
    providers: List[ProviderStatus]
    total: int
    healthy: int


class RateLimitInfo(BaseModel):
    """Rate limit information"""
    limit: int
    remaining: int
    reset: int
    limit_type: str


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    message: str
    status_code: int
    details: Optional[Dict[str, Any]] = None
