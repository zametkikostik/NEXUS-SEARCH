"""
IPFS Models
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class IPFSStoreRequest(BaseModel):
    """Request to store data in IPFS"""
    data: Any = Field(..., description="Data to store (JSON-serializable)")
    pin: bool = Field(default=True, description="Whether to pin the content")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")


class IPFSStoreResponse(BaseModel):
    """Response after storing data in IPFS"""
    cid: str = Field(..., description="Content Identifier (CID)")
    gateway_url: str = Field(..., description="Public gateway URL")
    size: int = Field(..., description="Data size in bytes")
    pinned: bool = Field(..., description="Whether content is pinned")


class IPFSRetrieveRequest(BaseModel):
    """Request to retrieve data from IPFS"""
    cid: str = Field(..., description="Content Identifier")


class IPFSRetrieveResponse(BaseModel):
    """Response with data from IPFS"""
    cid: str
    data: Any
    gateway_url: str


class IPFSStats(BaseModel):
    """IPFS node statistics"""
    connected: bool
    version: Optional[str] = None
    num_objects: Optional[int] = None
    repo_size: Optional[int] = None
    storage_used: Optional[int] = None
    error: Optional[str] = None


class SearchArchiveRequest(BaseModel):
    """Request to archive search results"""
    query: str = Field(..., description="Search query")
    results: List[Dict] = Field(..., description="Search results")
    metadata: Optional[Dict[str, Any]] = Field(default=None)
