"""
Brave Search Provider
"""
from typing import List, Dict, Any
import httpx
from core.config import get_settings
from core.logging import get_logger
from core.utils import create_session_with_retry
from providers.base import BaseProvider, SearchResult

settings = get_settings()
logger = get_logger(__name__)


class BraveProvider(BaseProvider):
    """Brave Search API provider"""
    
    name = "brave"
    base_url = "https://api.search.brave.com/res/v1/web/search"
    
    def __init__(self, timeout: int = 10, max_results: int = 10):
        super().__init__(timeout=timeout, max_results=max_results)
        self.api_key = settings.BRAVE_API_KEY
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[SearchResult]:
        """Search using Brave Search API"""
        if not self.api_key:
            logger.warning("Brave API key not configured")
            return []
        
        params = {
            "q": query,
            "count": min(limit, 20),
            "offset": offset,
            "safesearch": "off",
            "text_decorations": False,
            "search_lang": "en"
        }
        
        results = []
        
        try:
            async with await create_session_with_retry() as session:
                response = await session.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout,
                    headers={
                        "Accept": "application/json",
                        "X-Subscription-Token": self.api_key
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                results = await self._parse_results(data, query)
                
        except httpx.TimeoutException:
            logger.error("Brave search timeout", query=query)
        except httpx.HTTPStatusError as e:
            logger.error("Brave search error", status=e.response.status_code)
        except Exception as e:
            logger.error("Brave search failed", error=str(e))
        
        return results[:limit]
    
    async def _parse_results(
        self,
        response_data: Dict[str, Any],
        query: str
    ) -> List[SearchResult]:
        """Parse Brave API response"""
        results = []
        
        # Web results
        web_results = response_data.get("web", {}).get("results", [])
        
        for idx, item in enumerate(web_results[:self.max_results]):
            try:
                result = SearchResult(
                    title=self._truncate_text(item.get("title", ""), 200),
                    url=self._sanitize_url(item.get("url", "")),
                    snippet=self._truncate_text(item.get("description", ""), 500),
                    source=self.name,
                    rank=idx
                )
                results.append(result)
            except Exception as e:
                logger.warning("Failed to parse Brave result", error=str(e))
                continue
        
        return results
