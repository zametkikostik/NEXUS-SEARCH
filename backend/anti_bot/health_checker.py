"""
Health Checker for Providers
"""
import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import httpx
from core.config import get_settings
from core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ProviderHealth:
    """Provider health metrics"""
    provider: str
    status: HealthStatus = HealthStatus.UNKNOWN
    latency_ms: float = float('inf')
    success_rate: float = 0.0
    last_check: float = 0
    last_success: float = 0
    last_failure: float = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    consecutive_failures: int = 0
    response_times: List[float] = field(default_factory=list)
    
    @property
    def avg_latency_ms(self) -> float:
        """Calculate average latency"""
        if not self.response_times:
            return float('inf')
        return sum(self.response_times[-100:]) / len(self.response_times[-100:])
    
    def record_success(self, latency_ms: float) -> None:
        """Record successful request"""
        self.total_requests += 1
        self.successful_requests += 1
        self.last_success = time.time()
        self.last_check = time.time()
        self.consecutive_failures = 0
        self.response_times.append(latency_ms)
        
        # Keep only last 100 measurements
        if len(self.response_times) > 100:
            self.response_times = self.response_times[-100:]
        
        # Update success rate
        self.success_rate = self.successful_requests / self.total_requests
        
        # Update status
        if self.consecutive_failures < 3 and self.avg_latency_ms < 5000:
            self.status = HealthStatus.HEALTHY
        elif self.consecutive_failures < 5:
            self.status = HealthStatus.DEGRADED
    
    def record_failure(self) -> None:
        """Record failed request"""
        self.total_requests += 1
        self.failed_requests += 1
        self.last_failure = time.time()
        self.last_check = time.time()
        self.consecutive_failures += 1
        
        # Update success rate
        self.success_rate = self.successful_requests / self.total_requests if self.total_requests > 0 else 0
        
        # Update status
        if self.consecutive_failures >= 5:
            self.status = HealthStatus.UNHEALTHY
        elif self.consecutive_failures >= 3:
            self.status = HealthStatus.DEGRADED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "provider": self.provider,
            "status": self.status.value,
            "latency_ms": round(self.avg_latency_ms, 2) if self.avg_latency_ms < float('inf') else None,
            "success_rate": round(self.success_rate, 4),
            "last_check": self.last_check,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "consecutive_failures": self.consecutive_failures
        }


class HealthChecker:
    """Monitor provider health"""
    
    def __init__(self):
        self.health_metrics: Dict[str, ProviderHealth] = {}
        self._lock = asyncio.Lock()
        self._check_interval = 60  # seconds
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start health checker background task"""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._health_check_loop())
        logger.info("Health checker started")
    
    async def stop(self) -> None:
        """Stop health checker"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Health checker stopped")
    
    async def _health_check_loop(self) -> None:
        """Background health check loop"""
        while self._running:
            try:
                await asyncio.sleep(self._check_interval)
                # Health checks are done passively through request results
                # Active checks can be added here
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Health check loop error", error=str(e))
    
    async def record_result(
        self,
        provider: str,
        success: bool,
        latency_ms: float
    ) -> None:
        """Record request result"""
        async with self._lock:
            if provider not in self.health_metrics:
                self.health_metrics[provider] = ProviderHealth(provider=provider)
            
            health = self.health_metrics[provider]
            
            if success:
                health.record_success(latency_ms)
            else:
                health.record_failure()
    
    async def get_health(self, provider: str) -> Optional[ProviderHealth]:
        """Get health metrics for provider"""
        async with self._lock:
            return self.health_metrics.get(provider)
    
    async def get_all_health(self) -> Dict[str, ProviderHealth]:
        """Get all health metrics"""
        async with self._lock:
            return dict(self.health_metrics)
    
    async def get_healthy_providers(self) -> List[str]:
        """Get list of healthy providers"""
        async with self._lock:
            return [
                name for name, health in self.health_metrics.items()
                if health.status == HealthStatus.HEALTHY
            ]
    
    async def get_available_providers(self) -> List[str]:
        """Get list of available providers (not unhealthy)"""
        async with self._lock:
            return [
                name for name, health in self.health_metrics.items()
                if health.status != HealthStatus.UNHEALTHY
            ]
    
    async def get_provider_latency(self, provider: str) -> float:
        """Get provider latency"""
        async with self._lock:
            if provider not in self.health_metrics:
                return float('inf')
            return self.health_metrics[provider].avg_latency_ms
    
    async def get_provider_score(self, provider: str) -> float:
        """Calculate provider score for ranking"""
        async with self._lock:
            if provider not in self.health_metrics:
                return 0.5
            
            health = self.health_metrics[provider]
            
            # Score based on status
            status_scores = {
                HealthStatus.HEALTHY: 1.0,
                HealthStatus.DEGRADED: 0.5,
                HealthStatus.UNHEALTHY: 0.0,
                HealthStatus.UNKNOWN: 0.5
            }
            status_score = status_scores.get(health.status, 0.5)
            
            # Score based on success rate
            success_score = health.success_rate
            
            # Score based on latency (lower is better)
            latency = health.avg_latency_ms
            if latency == float('inf'):
                latency_score = 0.5
            elif latency < 500:
                latency_score = 1.0
            elif latency < 1000:
                latency_score = 0.8
            elif latency < 2000:
                latency_score = 0.6
            elif latency < 5000:
                latency_score = 0.4
            else:
                latency_score = 0.2
            
            return (status_score * 0.4 + success_score * 0.4 + latency_score * 0.2)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get health checker statistics"""
        return {
            "providers": {
                name: health.to_dict() 
                for name, health in self.health_metrics.items()
            },
            "total_providers": len(self.health_metrics),
            "healthy": sum(1 for h in self.health_metrics.values() if h.status == HealthStatus.HEALTHY),
            "degraded": sum(1 for h in self.health_metrics.values() if h.status == HealthStatus.DEGRADED),
            "unhealthy": sum(1 for h in self.health_metrics.values() if h.status == HealthStatus.UNHEALTHY)
        }


# Global health checker instance
health_checker = HealthChecker()


async def get_health_checker() -> HealthChecker:
    """Get health checker dependency"""
    return health_checker
