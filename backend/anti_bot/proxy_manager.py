"""
Proxy Manager with Rotation
"""
import asyncio
import random
import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import httpx
from core.config import get_settings
from core.logging import get_logger
from core.exceptions import NoAvailableProxiesException, ProxyException

settings = get_settings()
logger = get_logger(__name__)


class ProxyType(Enum):
    RESIDENTIAL = "residential"
    DATACENTER = "datacenter"
    TOR = "tor"


class ProxyStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    BANNED = "banned"
    UNKNOWN = "unknown"


@dataclass
class Proxy:
    """Proxy representation"""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    proxy_type: ProxyType = ProxyType.DATACENTER
    status: ProxyStatus = ProxyStatus.UNKNOWN
    latency: float = float('inf')
    last_check: float = 0
    failures: int = 0
    successes: int = 0
    last_used: float = 0
    country: Optional[str] = None
    
    @property
    def url(self) -> str:
        """Get proxy URL"""
        if self.username and self.password:
            return f"http://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"http://{self.host}:{self.port}"
    
    @property
    def dict(self) -> Dict[str, str]:
        """Get proxy as dict for httpx"""
        return {"http://": self.url, "https://": self.url}
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        total = self.successes + self.failures
        if total == 0:
            return 0.0
        return self.successes / total
    
    def mark_success(self, latency: float) -> None:
        """Mark successful request"""
        self.successes += 1
        self.failures = max(0, self.failures - 1)  # Decay failures
        self.latency = latency
        self.last_check = time.time()
        self.last_used = time.time()
        if self.failures < 3:
            self.status = ProxyStatus.HEALTHY
    
    def mark_failure(self, banned: bool = False) -> None:
        """Mark failed request"""
        self.failures += 1
        self.last_check = time.time()
        if banned:
            self.status = ProxyStatus.BANNED
        elif self.failures >= 5:
            self.status = ProxyStatus.UNHEALTHY
    
    def reset(self) -> None:
        """Reset proxy status"""
        self.failures = 0
        self.status = ProxyStatus.UNKNOWN
        self.latency = float('inf')


class ProxyManager:
    """Manage proxy rotation and health"""
    
    def __init__(self):
        self.proxies: List[Proxy] = []
        self._lock = asyncio.Lock()
        self._health_check_interval = 300  # 5 minutes
        self._last_health_check = 0
        self._initializing = False
    
    async def initialize(self) -> None:
        """Initialize proxy pool"""
        if self._initializing:
            return
        
        self._initializing = True
        try:
            # Load datacenter proxies from config
            if settings.DATACENTER_PROXIES:
                await self._load_datacenter_proxies()
            
            # Load from file
            await self._load_proxy_file()
            
            # Add Tor proxy if enabled
            if settings.TOR_PROXY_ENABLED:
                self.proxies.append(Proxy(
                    host=settings.TOR_PROXY_HOST,
                    port=settings.TOR_PROXY_PORT,
                    proxy_type=ProxyType.TOR
                ))
            
            # Initial health check
            if self.proxies:
                await self.health_check_all()
            
            logger.info("Proxy manager initialized", proxy_count=len(self.proxies))
        finally:
            self._initializing = False
    
    async def _load_datacenter_proxies(self) -> None:
        """Load datacenter proxies from config"""
        for proxy_str in settings.datacenter_proxies_list:
            try:
                proxy = self._parse_proxy_string(proxy_str)
                if proxy:
                    self.proxies.append(proxy)
            except Exception as e:
                logger.warning("Failed to parse proxy", proxy=proxy_str, error=str(e))
    
    async def _load_proxy_file(self) -> None:
        """Load proxies from file"""
        try:
            with open(settings.PROXY_LIST_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        proxy = self._parse_proxy_string(line)
                        if proxy:
                            self.proxies.append(proxy)
        except FileNotFoundError:
            logger.debug("Proxy file not found", file=settings.PROXY_LIST_FILE)
        except Exception as e:
            logger.error("Failed to load proxy file", error=str(e))
    
    def _parse_proxy_string(self, proxy_str: str) -> Optional[Proxy]:
        """Parse proxy string to Proxy object"""
        try:
            # Format: host:port or user:pass@host:port
            auth = None
            host_port = proxy_str
            
            if '@' in proxy_str:
                auth, host_port = proxy_str.split('@', 1)
            
            host, port = host_port.split(':', 1)
            
            username, password = None, None
            if auth:
                if ':' in auth:
                    username, password = auth.split(':', 1)
            
            return Proxy(
                host=host.strip(),
                port=int(port.strip()),
                username=username.strip() if username else None,
                password=password.strip() if password else None
            )
        except Exception:
            return None
    
    async def get_proxy(self, exclude_banned: bool = True) -> Optional[Proxy]:
        """Get next available proxy"""
        async with self._lock:
            if not self.proxies:
                return None
            
            # Filter available proxies
            available = []
            for proxy in self.proxies:
                if exclude_banned and proxy.status == ProxyStatus.BANNED:
                    continue
                
                # Skip recently used proxies (cooldown)
                if time.time() - proxy.last_used < 10:
                    continue
                
                available.append(proxy)
            
            if not available:
                # Fallback: use any non-banned proxy
                available = [
                    p for p in self.proxies 
                    if p.status != ProxyStatus.BANNED or not exclude_banned
                ]
            
            if not available:
                return None
            
            # Weighted random selection (prefer healthy, low latency)
            weighted = []
            for proxy in available:
                weight = 1.0
                if proxy.status == ProxyStatus.HEALTHY:
                    weight *= 2.0
                if proxy.latency < float('inf'):
                    weight *= (100 / (proxy.latency + 1))
                weight *= proxy.success_rate + 0.1
                weighted.append((proxy, weight))
            
            total_weight = sum(w for _, w in weighted)
            if total_weight == 0:
                return random.choice(available)
            
            r = random.uniform(0, total_weight)
            cumulative = 0
            for proxy, weight in weighted:
                cumulative += weight
                if r <= cumulative:
                    return proxy
            
            return weighted[-1][0]
    
    async def health_check_all(self) -> Dict[str, int]:
        """Health check all proxies"""
        results = {"healthy": 0, "unhealthy": 0, "banned": 0}
        
        async def check_proxy(proxy: Proxy) -> None:
            try:
                start = time.time()
                async with httpx.AsyncClient(
                    proxies=proxy.dict,
                    timeout=httpx.Timeout(10)
                ) as client:
                    response = await client.get("https://httpbin.org/ip")
                    latency = time.time() - start
                    
                    if response.status_code == 200:
                        proxy.mark_success(latency)
                        results["healthy"] += 1
                    else:
                        proxy.mark_failure()
                        results["unhealthy"] += 1
            except Exception as e:
                proxy.mark_failure(banned="403" in str(e) or "ban" in str(e).lower())
                if proxy.status == ProxyStatus.BANNED:
                    results["banned"] += 1
                else:
                    results["unhealthy"] += 1
        
        tasks = [check_proxy(proxy) for proxy in self.proxies]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        self._last_health_check = time.time()
        logger.info("Proxy health check completed", **results)
        
        return results
    
    async def get_healthy_proxy_count(self) -> int:
        """Get count of healthy proxies"""
        return sum(1 for p in self.proxies if p.status == ProxyStatus.HEALTHY)
    
    async def add_proxy(self, proxy: Proxy) -> None:
        """Add new proxy to pool"""
        async with self._lock:
            # Check if already exists
            for p in self.proxies:
                if p.host == proxy.host and p.port == proxy.port:
                    return
            self.proxies.append(proxy)
            logger.info("Proxy added", host=proxy.host, port=proxy.port)
    
    async def remove_proxy(self, host: str, port: int) -> None:
        """Remove proxy from pool"""
        async with self._lock:
            self.proxies = [
                p for p in self.proxies 
                if not (p.host == host and p.port == port)
            ]
            logger.info("Proxy removed", host=host, port=port)
    
    async def mark_proxy_banned(self, proxy: Proxy) -> None:
        """Mark proxy as banned"""
        proxy.mark_failure(banned=True)
        logger.warning("Proxy marked as banned", host=proxy.host, port=proxy.port)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get proxy pool statistics"""
        total = len(self.proxies)
        healthy = sum(1 for p in self.proxies if p.status == ProxyStatus.HEALTHY)
        unhealthy = sum(1 for p in self.proxies if p.status == ProxyStatus.UNHEALTHY)
        banned = sum(1 for p in self.proxies if p.status == ProxyStatus.BANNED)
        unknown = sum(1 for p in self.proxies if p.status == ProxyStatus.UNKNOWN)
        
        avg_latency = sum(
            p.latency for p in self.proxies if p.latency < float('inf')
        ) / max(1, healthy)
        
        return {
            "total": total,
            "healthy": healthy,
            "unhealthy": unhealthy,
            "banned": banned,
            "unknown": unknown,
            "avg_latency_ms": round(avg_latency * 1000, 2) if healthy > 0 else None
        }


# Global proxy manager instance
proxy_manager = ProxyManager()


async def get_proxy_manager() -> ProxyManager:
    """Get proxy manager dependency"""
    if not proxy_manager.proxies:
        await proxy_manager.initialize()
    return proxy_manager
