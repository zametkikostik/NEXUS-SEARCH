"""
Request Session with Anti-Bot Features
"""
import asyncio
import random
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import httpx
from fake_useragent import UserAgent
from core.config import get_settings
from core.logging import get_logger
from core.utils import get_random_user_agent
from anti_bot.proxy_manager import Proxy, get_proxy_manager
from anti_bot.circuit_breaker import get_circuit_breaker
from anti_bot.health_checker import health_checker

settings = get_settings()
logger = get_logger(__name__)


@dataclass
class RequestConfig:
    """Request configuration"""
    timeout: int = 30
    max_retries: int = 3
    follow_redirects: bool = True
    verify_ssl: bool = True
    use_proxy: bool = True
    rotate_user_agent: bool = True


class AntiBotSession:
    """HTTP session with anti-bot features"""
    
    def __init__(self, config: Optional[RequestConfig] = None):
        self.config = config or RequestConfig()
        self._session: Optional[httpx.AsyncClient] = None
        self._ua = UserAgent() if self.config.rotate_user_agent else None
        self._proxy_manager = None
        self._request_count = 0
    
    async def __aenter__(self):
        await self._create_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def _create_session(self) -> None:
        """Create HTTP session"""
        if self._session and not self._session.is_closed:
            return
        
        headers = self._generate_headers()
        
        self._session = httpx.AsyncClient(
            headers=headers,
            timeout=httpx.Timeout(self.config.timeout),
            follow_redirects=self.config.follow_redirects,
            verify=self.config.verify_ssl,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=50),
        )
        
        if self.config.use_proxy:
            self._proxy_manager = await get_proxy_manager()
    
    async def close(self) -> None:
        """Close session"""
        if self._session and not self._session.is_closed:
            await self._session.aclose()
            self._session = None
    
    def _generate_headers(self) -> Dict[str, str]:
        """Generate random headers"""
        user_agent = self._ua.random if self._ua else get_random_user_agent()
        
        return {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
    
    def _update_headers_for_request(self, url: str) -> None:
        """Update headers for specific request"""
        if self._session:
            self._session.headers["Referer"] = f"https://{url.split('/')[2]}/"
    
    async def _get_proxy(self) -> Optional[Proxy]:
        """Get proxy for request"""
        if not self._proxy_manager:
            return None
        return await self._proxy_manager.get_proxy()
    
    async def _apply_jitter(self) -> None:
        """Apply random delay jitter"""
        jitter = random.uniform(0.1, 0.5)
        await asyncio.sleep(jitter)
    
    async def request(
        self,
        method: str,
        url: str,
        provider: Optional[str] = None,
        **kwargs
    ) -> httpx.Response:
        """Make request with anti-bot features"""
        if not self._session:
            await self._create_session()
        
        self._update_headers_for_request(url)
        await self._apply_jitter()
        
        last_exception = None
        retries = 0
        
        while retries < self.config.max_retries:
            try:
                # Get proxy if enabled
                proxy = None
                if self.config.use_proxy and self._proxy_manager:
                    proxy = await self._proxy_manager.get_proxy()
                    if proxy:
                        # Update proxy for this request
                        self._session.proxies = proxy.dict
                
                # Make request
                start_time = time.time()
                response = await self._session.request(method, url, **kwargs)
                latency_ms = (time.time() - start_time) * 1000
                
                # Record health metrics
                if provider:
                    await health_checker.record_result(
                        provider,
                        success=response.status_code < 400,
                        latency_ms=latency_ms
                    )
                    
                    # Check for ban indicators
                    if self._is_ban_indicator(response):
                        if proxy and self._proxy_manager:
                            await self._proxy_manager.mark_proxy_banned(proxy)
                        raise httpx.HTTPStatusError(
                            "Possible ban detected",
                            request=response.request,
                            response=response
                        )
                
                # Mark proxy success
                if proxy and self._proxy_manager and response.status_code < 400:
                    await self._proxy_manager._lock.__aenter__()
                    try:
                        proxy.mark_success(latency_ms / 1000)
                    finally:
                        await self._proxy_manager._lock.__aexit__(None, None, None)
                
                response.raise_for_status()
                return response
                
            except httpx.HTTPStatusError as e:
                last_exception = e
                if e.response.status_code in (429, 403, 503):
                    # Rate limited or banned - use new proxy
                    retries += 1
                    if retries < self.config.max_retries:
                        backoff = (2 ** retries) + random.uniform(0, 1)
                        logger.warning(
                            "Request rate limited, retrying with new proxy",
                            url=url,
                            status=e.response.status_code,
                            retry=retries,
                            backoff=backoff
                        )
                        await asyncio.sleep(backoff)
                        continue
                break
                
            except httpx.TimeoutException as e:
                last_exception = e
                retries += 1
                if retries < self.config.max_retries:
                    backoff = (2 ** retries) + random.uniform(0, 1)
                    logger.warning(
                        "Request timeout, retrying",
                        url=url,
                        retry=retries,
                        backoff=backoff
                    )
                    await asyncio.sleep(backoff)
                    continue
                break
                
            except Exception as e:
                last_exception = e
                retries += 1
                if retries < self.config.max_retries:
                    backoff = (2 ** retries) + random.uniform(0, 1)
                    logger.warning(
                        "Request failed, retrying",
                        url=url,
                        error=str(e),
                        retry=retries
                    )
                    await asyncio.sleep(backoff)
                    continue
                break
        
        # All retries exhausted
        if provider and last_exception:
            await health_checker.record_result(provider, success=False, latency_ms=0)
        
        if last_exception:
            raise last_exception
        
        raise httpx.RequestError("All retries exhausted")
    
    def _is_ban_indicator(self, response: httpx.Response) -> bool:
        """Check if response indicates a ban"""
        # Check status code
        if response.status_code in (403, 429, 503):
            return True
        
        # Check content for ban indicators
        content = response.text.lower()
        ban_indicators = [
            "access denied",
            "blocked",
            "captcha",
            "suspicious traffic",
            "automated request",
            "rate limit",
            "too many requests"
        ]
        
        return any(indicator in content for indicator in ban_indicators)
    
    async def get(self, url: str, provider: Optional[str] = None, **kwargs) -> httpx.Response:
        """GET request"""
        return await self.request("GET", url, provider=provider, **kwargs)
    
    async def post(self, url: str, provider: Optional[str] = None, **kwargs) -> httpx.Response:
        """POST request"""
        return await self.request("POST", url, provider=provider, **kwargs)
    
    def get_request_count(self) -> int:
        """Get total request count"""
        return self._request_count


async def create_anti_bot_session(
    timeout: int = 30,
    max_retries: int = 3,
    use_proxy: bool = True
) -> AntiBotSession:
    """Create anti-bot session"""
    config = RequestConfig(
        timeout=timeout,
        max_retries=max_retries,
        use_proxy=use_proxy
    )
    session = AntiBotSession(config)
    await session._create_session()
    return session
