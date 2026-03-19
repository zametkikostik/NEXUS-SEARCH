"""
Health Check Endpoints
"""
import time
from fastapi import APIRouter
from core.config import get_settings
from core.cache import cache
from anti_bot.health_checker import health_checker
from api.models import HealthResponse, HealthStatus, ProvidersResponse, ProviderStatus
from providers.aggregator import get_aggregator

settings = get_settings()
router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Overall health check
    """
    services = {}
    overall_status = HealthStatus.HEALTHY
    
    # Check cache
    cache_healthy = cache.is_connected
    services["cache"] = cache_healthy
    if not cache_healthy:
        overall_status = HealthStatus.DEGRADED
    
    # Check providers
    try:
        aggregator = await get_aggregator()
        providers = aggregator.get_available_providers()
        services["providers"] = len(providers) > 0
        if not services["providers"]:
            overall_status = HealthStatus.DEGRADED
    except:
        services["providers"] = False
        overall_status = HealthStatus.DEGRADED
    
    # Check IPFS
    from ipfs.client import ipfs_client
    ipfs_healthy = ipfs_client._connected
    services["ipfs"] = ipfs_healthy
    
    return HealthResponse(
        status=overall_status,
        version="1.0.0",
        timestamp=time.time(),
        services=services
    )


@router.get("/health/live")
async def liveness_check():
    """
    Liveness probe - is the service running?
    """
    return {
        "status": "alive",
        "timestamp": time.time()
    }


@router.get("/health/ready")
async def readiness_check():
    """
    Readiness probe - is the service ready to handle requests?
    """
    ready = True
    checks = {}
    
    # Cache
    checks["cache"] = cache.is_connected
    if not checks["cache"]:
        ready = False
    
    # Proxy manager
    from anti_bot.proxy_manager import proxy_manager
    proxy_stats = proxy_manager.get_stats()
    checks["proxies"] = proxy_stats["total"] > 0
    checks["healthy_proxies"] = proxy_stats["healthy"]
    
    # Providers
    try:
        aggregator = await get_aggregator()
        providers = aggregator.get_available_providers()
        checks["providers"] = len(providers)
    except:
        checks["providers"] = 0
        ready = False
    
    return {
        "ready": ready,
        "checks": checks,
        "timestamp": time.time()
    }


@router.get("/providers", response_model=ProvidersResponse)
async def get_providers_status():
    """
    Get status of all search providers
    """
    aggregator = await get_aggregator()
    provider_status = aggregator.get_provider_status()
    
    # Get health metrics
    all_health = await health_checker.get_all_health()
    
    providers = []
    healthy_count = 0
    
    for name, status in provider_status.items():
        health = all_health.get(name)
        
        provider = ProviderStatus(
            name=name,
            enabled=status.get("enabled", False),
            healthy=health.status.value == "healthy" if health else False,
            latency_ms=health.avg_latency_ms if health and health.avg_latency_ms < float('inf') else None,
            success_rate=health.success_rate if health else None
        )
        
        providers.append(provider)
        
        if provider.healthy:
            healthy_count += 1
    
    return ProvidersResponse(
        providers=providers,
        total=len(providers),
        healthy=healthy_count
    )


@router.get("/metrics")
async def get_metrics():
    """
    Get Prometheus-style metrics
    """
    import json
    
    # Health metrics
    health_stats = health_checker.get_stats()
    
    # Proxy metrics
    from anti_bot.proxy_manager import proxy_manager
    proxy_stats = proxy_manager.get_stats()
    
    # Cache metrics
    cache_metrics = {
        "connected": cache.is_connected
    }
    
    metrics = {
        "health": health_stats,
        "proxies": proxy_stats,
        "cache": cache_metrics,
        "timestamp": time.time()
    }
    
    return metrics
