"""
Provider Aggregator - Coordinates multiple search providers
"""
import asyncio
import time
from typing import List, Dict, Any, Optional, Type
from core.config import get_settings
from core.logging import get_logger
from core.utils import merge_results, hash_query
from core.exceptions import SearchException, ProviderException
from providers.base import BaseProvider, SearchResult
from providers.google import GoogleProvider, GoogleOrganicProvider
from providers.duckduckgo import DuckDuckGoProvider, DuckDuckGoAPIProvider
from providers.brave import BraveProvider
from providers.yandex import YandexProvider
from providers.dzen import DzenProvider
from providers.reddit import RedditProvider, RedditPostsProvider
from anti_bot.circuit_breaker import get_circuit_breaker, CircuitBreakerOpenException
from anti_bot.health_checker import health_checker

settings = get_settings()
logger = get_logger(__name__)


# Provider registry
PROVIDER_REGISTRY: Dict[str, Type[BaseProvider]] = {
    "google": GoogleProvider,
    "google_organic": GoogleOrganicProvider,
    "duckduckgo": DuckDuckGoProvider,
    "duckduckgo_api": DuckDuckGoAPIProvider,
    "brave": BraveProvider,
    "yandex": YandexProvider,
    "dzen": DzenProvider,
    "reddit": RedditProvider,
    "reddit_posts": RedditPostsProvider,
}


class ProviderAggregator:
    """Aggregate search results from multiple providers"""
    
    def __init__(self):
        self.providers: Dict[str, BaseProvider] = {}
        self._initialized = False
    
    def _init_providers(self) -> None:
        """Initialize enabled providers"""
        if self._initialized:
            return
        
        for name, provider_class in PROVIDER_REGISTRY.items():
            try:
                provider = provider_class()
                if provider.is_enabled():
                    self.providers[name] = provider
                    logger.debug(f"Initialized provider: {name}")
            except Exception as e:
                logger.warning(f"Failed to initialize provider {name}", error=str(e))
        
        self._initialized = True
        logger.info(f"Initialized {len(self.providers)} providers")
    
    async def search(
        self,
        query: str,
        providers: Optional[List[str]] = None,
        limit: int = 10,
        timeout: Optional[float] = None
    ) -> List[SearchResult]:
        """
        Search across multiple providers
        
        Args:
            query: Search query
            providers: List of provider names (None = all enabled)
            limit: Maximum total results
            timeout: Overall timeout in seconds
        
        Returns:
            Merged and deduplicated search results
        """
        self._init_providers()
        
        if not query or not query.strip():
            raise SearchException("Query cannot be empty")
        
        # Determine which providers to use
        if providers:
            target_providers = [
                name for name in providers 
                if name in self.providers
            ]
        else:
            target_providers = list(self.providers.keys())
        
        if not target_providers:
            raise SearchException("No providers available")
        
        # Search concurrently
        all_results = []
        provider_timeout = timeout or settings.PROVIDER_TIMEOUT_DEFAULT
        
        async def search_provider(name: str) -> List[SearchResult]:
            """Search single provider with circuit breaker"""
            try:
                cb = await get_circuit_breaker(name)
                
                async def do_search():
                    provider = self.providers[name]
                    start = time.time()
                    results = await provider.search(query, limit=limit)
                    latency = (time.time() - start) * 1000
                    
                    # Record health metrics
                    await health_checker.record_result(name, success=True, latency_ms=latency)
                    
                    return results
                
                return await cb.call(do_search)
                
            except CircuitBreakerOpenException as e:
                logger.warning(f"Circuit breaker open for {name}", retry_after=e.details.get("retry_after"))
                return []
            except Exception as e:
                logger.error(f"Provider {name} failed", error=str(e))
                await health_checker.record_result(name, success=False, latency_ms=0)
                return []
        
        # Run all provider searches concurrently
        tasks = [search_provider(name) for name in target_providers]
        provider_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect all results
        for result in provider_results:
            if isinstance(result, list):
                all_results.extend(result)
        
        if not all_results:
            logger.warning("No results from any provider", query=query)
            return []
        
        # Merge and deduplicate
        merged = merge_results(
            [r.to_dict() for r in all_results],
            query
        )
        
        # Convert back to SearchResult objects
        final_results = [SearchResult.from_dict(r) for r in merged[:limit]]
        
        logger.info(
            f"Search completed",
            query=query,
            providers_used=len(target_providers),
            total_results=len(final_results)
        )
        
        return final_results
    
    async def search_single(
        self,
        provider_name: str,
        query: str,
        limit: int = 10
    ) -> List[SearchResult]:
        """Search using single provider"""
        self._init_providers()
        
        if provider_name not in self.providers:
            raise ProviderException(
                provider=provider_name,
                message=f"Unknown provider: {provider_name}"
            )
        
        provider = self.providers[provider_name]
        return await provider.search(query, limit=limit)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        self._init_providers()
        return list(self.providers.keys())
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers"""
        self._init_providers()
        status = {}
        
        for name, provider in self.providers.items():
            status[name] = {
                "enabled": provider.is_enabled(),
                "timeout": provider.get_timeout(),
                "max_results": provider.max_results
            }
        
        return status


# Global aggregator instance
aggregator = ProviderAggregator()


async def get_aggregator() -> ProviderAggregator:
    """Get provider aggregator dependency"""
    return aggregator
