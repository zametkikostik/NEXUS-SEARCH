"""
IPFS API Endpoints
"""
import json
from fastapi import APIRouter, HTTPException
from core.logging import get_logger
from ipfs.client import get_ipfs_client
from ipfs.models import (
    IPFSStoreRequest,
    IPFSStoreResponse,
    IPFSRetrieveRequest,
    IPFSRetrieveResponse,
    IPFSStats,
    SearchArchiveRequest
)

logger = get_logger(__name__)
router = APIRouter(prefix="/ipfs", tags=["IPFS"])


@router.post("/store", response_model=IPFSStoreResponse)
async def store_data(request: IPFSStoreRequest):
    """
    Store data in IPFS
    
    Returns CID and gateway URL for stored data
    """
    try:
        ipfs = await get_ipfs_client()
        
        # Store data
        cid = await ipfs.add(request.data, pin=request.pin)
        
        # Get gateway URL
        gateway_url = await ipfs.get_gateway_url(cid)
        
        # Calculate size
        if isinstance(request.data, str):
            size = len(request.data.encode('utf-8'))
        elif isinstance(request.data, (dict, list)):
            size = len(json.dumps(request.data).encode('utf-8'))
        else:
            size = len(request.data)
        
        return IPFSStoreResponse(
            cid=cid,
            gateway_url=gateway_url,
            size=size,
            pinned=request.pin
        )
        
    except Exception as e:
        logger.error("Failed to store in IPFS", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store data: {str(e)}"
        )


@router.post("/retrieve", response_model=IPFSRetrieveResponse)
async def retrieve_data(request: IPFSRetrieveRequest):
    """
    Retrieve data from IPFS by CID
    """
    try:
        ipfs = await get_ipfs_client()
        
        # Get data
        data = await ipfs.get_json(request.cid)
        
        # Get gateway URL
        gateway_url = await ipfs.get_gateway_url(request.cid)
        
        return IPFSRetrieveResponse(
            cid=request.cid,
            data=data,
            gateway_url=gateway_url
        )
        
    except Exception as e:
        logger.error("Failed to retrieve from IPFS", cid=request.cid, error=str(e))
        raise HTTPException(
            status_code=404,
            detail=f"Failed to retrieve data: {str(e)}"
        )


@router.get("/retrieve/{cid}")
async def retrieve_data_raw(cid: str):
    """
    Retrieve raw data from IPFS by CID
    """
    try:
        ipfs = await get_ipfs_client()
        
        # Get data
        data = await ipfs.get_json(cid)
        
        return data
        
    except Exception as e:
        logger.error("Failed to retrieve from IPFS", cid=cid, error=str(e))
        raise HTTPException(
            status_code=404,
            detail=f"Failed to retrieve data: {str(e)}"
        )


@router.post("/archive/search", response_model=IPFSStoreResponse)
async def archive_search_results(request: SearchArchiveRequest):
    """
    Archive search results to IPFS
    
    Stores query, results, and metadata
    """
    try:
        ipfs = await get_ipfs_client()
        
        # Store search results
        cid = await ipfs.store_search_results(
            query=request.query,
            results=request.results,
            metadata=request.metadata
        )
        
        gateway_url = await ipfs.get_gateway_url(cid)
        
        # Calculate approximate size
        size = len(json.dumps({
            "query": request.query,
            "results": request.results
        }).encode('utf-8'))
        
        return IPFSStoreResponse(
            cid=cid,
            gateway_url=gateway_url,
            size=size,
            pinned=True
        )
        
    except Exception as e:
        logger.error("Failed to archive search results", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to archive: {str(e)}"
        )


@router.get("/stats", response_model=IPFSStats)
async def get_ipfs_stats():
    """
    Get IPFS node statistics
    """
    try:
        ipfs = await get_ipfs_client()
        stats = await ipfs.get_stats()
        return IPFSStats(**stats)
        
    except Exception as e:
        logger.error("Failed to get IPFS stats", error=str(e))
        return IPFSStats(
            connected=False,
            error=str(e)
        )


@router.get("/pin/ls")
async def list_pins():
    """
    List all pinned CIDs
    """
    try:
        ipfs = await get_ipfs_client()
        pins = await ipfs.pin_ls()
        
        return {
            "pins": pins,
            "count": len(pins)
        }
        
    except Exception as e:
        logger.error("Failed to list pins", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list pins: {str(e)}"
        )


@router.post("/pin/add")
async def pin_content(cid: str):
    """
    Pin content to prevent garbage collection
    """
    try:
        ipfs = await get_ipfs_client()
        success = await ipfs.pin(cid)
        
        return {
            "success": success,
            "cid": cid
        }
        
    except Exception as e:
        logger.error("Failed to pin content", cid=cid, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to pin: {str(e)}"
        )


@router.post("/pin/rm")
async def unpin_content(cid: str):
    """
    Unpin content
    """
    try:
        ipfs = await get_ipfs_client()
        success = await ipfs.unpin(cid)
        
        return {
            "success": success,
            "cid": cid
        }
        
    except Exception as e:
        logger.error("Failed to unpin content", cid=cid, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to unpin: {str(e)}"
        )
