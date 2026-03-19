"""
IPFS Client for decentralized storage
"""
import json
import asyncio
from typing import Optional, Dict, Any, Union
from pathlib import Path
import httpx
from core.config import get_settings
from core.logging import get_logger
from core.exceptions import IPFSUploadException, IPFSDownloadException

settings = get_settings()
logger = get_logger(__name__)


class IPFSClient:
    """IPFS HTTP client for Kubo daemon"""
    
    def __init__(self):
        self.host = settings.IPFS_HOST
        self.port = settings.IPFS_PORT
        self.gateway = settings.IPFS_GATEWAY
        self.api_url = f"http://{self.host}:{self.port}/api/v0"
        self._client: Optional[httpx.AsyncClient] = None
        self._connected = False
    
    async def connect(self) -> bool:
        """Connect to IPFS node"""
        try:
            self._client = httpx.AsyncClient(
                base_url=self.api_url,
                timeout=httpx.Timeout(60)
            )
            
            # Test connection
            response = await self._client.get("/version")
            if response.status_code == 200:
                self._connected = True
                version = response.json().get("Version", "unknown")
                logger.info("Connected to IPFS", version=version)
                return True
            
            return False
            
        except Exception as e:
            logger.error("Failed to connect to IPFS", error=str(e))
            self._connected = False
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from IPFS"""
        if self._client:
            await self._client.aclose()
            self._connected = False
    
    async def add(
        self,
        data: Union[str, bytes, dict, list],
        pin: bool = True
    ) -> str:
        """
        Add data to IPFS
        
        Args:
            data: Data to add (string, bytes, or JSON-serializable)
            pin: Whether to pin the content
        
        Returns:
            CID (Content Identifier)
        """
        if not self._connected:
            if not await self.connect():
                raise IPFSUploadException("Cannot connect to IPFS")
        
        try:
            # Convert data to bytes
            if isinstance(data, (dict, list)):
                content = json.dumps(data, separators=(',', ':')).encode('utf-8')
            elif isinstance(data, str):
                content = data.encode('utf-8')
            else:
                content = data
            
            # Upload to IPFS
            files = {"file": ("data.json", content)}
            params = {"pin": "true"} if pin else {}
            
            response = await self._client.post("/add", files=files, params=params)
            response.raise_for_status()
            
            result = response.json()
            cid = result.get("Hash")
            
            if not cid:
                raise IPFSUploadException("No CID in response")
            
            logger.info("Data added to IPFS", cid=cid, size=len(content))
            return cid
            
        except httpx.HTTPStatusError as e:
            logger.error("IPFS upload failed", status=e.response.status_code)
            raise IPFSUploadException(f"HTTP error: {e.response.status_code}")
        except Exception as e:
            logger.error("IPFS upload failed", error=str(e))
            raise IPFSUploadException(str(e))
    
    async def get(self, cid: str) -> bytes:
        """
        Get data from IPFS
        
        Args:
            cid: Content Identifier
        
        Returns:
            Raw bytes
        """
        if not self._connected:
            if not await self.connect():
                raise IPFSDownloadException(cid)
        
        try:
            response = await self._client.get("/cat", params={"arg": cid})
            response.raise_for_status()
            
            logger.info("Data retrieved from IPFS", cid=cid, size=len(response.content))
            return response.content
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise IPFSDownloadException(cid)
            logger.error("IPFS download failed", status=e.response.status_code)
            raise IPFSDownloadException(cid)
        except Exception as e:
            logger.error("IPFS download failed", error=str(e))
            raise IPFSDownloadException(cid)
    
    async def get_json(self, cid: str) -> Any:
        """
        Get JSON data from IPFS
        
        Args:
            cid: Content Identifier
        
        Returns:
            Parsed JSON data
        """
        content = await self.get(cid)
        return json.loads(content.decode('utf-8'))
    
    async def pin(self, cid: str) -> bool:
        """Pin content to prevent garbage collection"""
        if not self._connected:
            if not await self.connect():
                return False
        
        try:
            response = await self._client.post("/pin/add", params={"arg": cid})
            response.raise_for_status()
            
            logger.info("Content pinned", cid=cid)
            return True
            
        except Exception as e:
            logger.error("Failed to pin content", cid=cid, error=str(e))
            return False
    
    async def unpin(self, cid: str) -> bool:
        """Unpin content"""
        if not self._connected:
            if not await self.connect():
                return False
        
        try:
            response = await self._client.post("/pin/rm", params={"arg": cid})
            response.raise_for_status()
            
            logger.info("Content unpinned", cid=cid)
            return True
            
        except Exception as e:
            logger.error("Failed to unpin content", cid=cid, error=str(e))
            return False
    
    async def pin_ls(self) -> list:
        """List all pinned CIDs"""
        if not self._connected:
            if not await self.connect():
                return []
        
        try:
            response = await self._client.get("/pin/ls")
            response.raise_for_status()
            
            result = response.json()
            pins = list(result.get("Keys", {}).keys())
            
            logger.info("Listed pinned CIDs", count=len(pins))
            return pins
            
        except Exception as e:
            logger.error("Failed to list pins", error=str(e))
            return []
    
    async def get_gateway_url(self, cid: str) -> str:
        """Get public gateway URL for CID"""
        return f"{self.gateway}{cid}"
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get IPFS node statistics"""
        if not self._connected:
            if not await self.connect():
                return {}
        
        try:
            # Get repo stats
            response = await self._client.get("/repo/stat")
            response.raise_for_status()
            stats = response.json()
            
            # Get repo version
            version_response = await self._client.get("/version")
            version = version_response.json().get("Version", "unknown")
            
            return {
                "connected": True,
                "version": version,
                "num_objects": stats.get("NumObjects", 0),
                "repo_size": stats.get("RepoSize", 0),
                "repo_path": stats.get("RepoPath", ""),
                "storage_used": stats.get("StorageUsed", 0)
            }
            
        except Exception as e:
            logger.error("Failed to get IPFS stats", error=str(e))
            return {"connected": False, "error": str(e)}
    
    async def store_search_results(
        self,
        query: str,
        results: list,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Store search results in IPFS
        
        Args:
            query: Search query
            results: Search results
            metadata: Optional metadata
        
        Returns:
            CID of stored data
        """
        import time
        
        data = {
            "query": query,
            "results": results,
            "timestamp": time.time(),
            "version": "1.0",
            **(metadata or {})
        }
        
        cid = await self.add(data)
        logger.info("Search results stored in IPFS", cid=cid, query=query)
        
        return cid


# Global IPFS client instance
ipfs_client = IPFSClient()


async def get_ipfs_client() -> IPFSClient:
    """Get IPFS client dependency"""
    if not ipfs_client._connected:
        await ipfs_client.connect()
    return ipfs_client
