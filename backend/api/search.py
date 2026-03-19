"""
Search API Endpoint
"""
import time
from typing import Optional, List
from fastapi import APIRouter, Query, Depends, HTTPException
from core.config import get_settings
from core.logging import get_logger
from core.utils import hash_query
from core.cache import get_cache, CacheClient
from core.exceptions import SearchException
from filters.content_filter import get_content_filter
from providers.aggregator import get_aggregator
from ipfs.client import get_ipfs_client
from api.models import SearchRequest, SearchResponse

settings = get_settings()
logger = get_logger(__name__)
router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    providers: Optional[str] = Query(None, description="Comma-separated provider names"),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
    timeout: Optional[float] = Query(None, description="Timeout in seconds"),
    cache_enabled: bool = Query(True, description="Use cache"),
    filter_content: bool = Query(True, description="Filter content"),
    store_ipfs: bool = Query(False, description="Store in IPFS")
):
    """
    Search across multiple providers
    """
    start_time = time.time()
    
    # Parse providers
    provider_list = None
    if providers:
        provider_list = [p.strip() for p in providers.split(",")]
    
    # Check cache
    cached_results = None
    query_hash = hash_query(q)
    
    if cache_enabled:
        cache_client = await get_cache()
        cached_results = await cache_client.search_cache_get(query_hash)
        
        if cached_results:
            logger.info("Cache hit", query=q)
            return SearchResponse(
                query=q,
                results=cached_results,
                total=len(cached_results),
                providers_used=[],
                time_ms=0,
                cached=True
            )
    
    # Perform search
    aggregator = await get_aggregator()
    
    try:
        results = await aggregator.search(
            query=q,
            providers=provider_list,
            limit=limit,
            timeout=timeout
        )
    except Exception as e:
        logger.error("Search failed", query=q, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )
    
    if not results:
        return SearchResponse(
            query=q,
            results=[],
            total=0,
            providers_used=provider_list or [],
            time_ms=(time.time() - start_time) * 1000
        )
    
    # Convert to dicts
    results_dicts = [r.to_dict() for r in results]
    
    # Filter content
    if filter_content and settings.FILTER_ENABLED:
        content_filter = get_content_filter()
        results_dicts = content_filter.filter_results(results_dicts)
    
    # Cache results
    if cache_enabled:
        cache_client = await get_cache()
        is_news = any(word in q.lower() for word in ["news", "today", "latest", "breaking"])
        await cache_client.search_cache_set(
            query_hash,
            results_dicts,
            is_news=is_news
        )
    
    # Store in IPFS
    ipfs_cid = None
    if store_ipfs:
        try:
            ipfs = await get_ipfs_client()
            ipfs_cid = await ipfs.store_search_results(
                query=q,
                results=results_dicts
            )
        except Exception as e:
            logger.warning("Failed to store in IPFS", error=str(e))
    
    # Get providers used
    providers_used = list(set(r.get("source", "") for r in results_dicts))
    
    duration_ms = (time.time() - start_time) * 1000
    
    logger.info(
        "Search completed",
        query=q,
        results=len(results_dicts),
        duration_ms=round(duration_ms, 2)
    )
    
    return SearchResponse(
        query=q,
        results=results_dicts,
        total=len(results_dicts),
        providers_used=providers_used,
        time_ms=duration_ms,
        cached=False,
        ipfs_cid=ipfs_cid
    )


@router.get("/providers")
async def get_providers():
    """Get available search providers"""
    aggregator = await get_aggregator()
    providers = aggregator.get_available_providers()
    status = aggregator.get_provider_status()
    
    return {
        "providers": providers,
        "status": status
    }
