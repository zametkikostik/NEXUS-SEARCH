"""
Google Search Provider
"""
import json
from typing import List, Dict, Any
import httpx
from core.config import get_settings
from core.logging import get_logger
from core.utils import create_session_with_retry
from providers.base import BaseProvider, SearchResult

settings = get_settings()
logger = get_logger(__name__)


class GoogleProvider(BaseProvider):
    """Google Custom Search API provider"""
    
    name = "google"
    base_url = "https://www.googleapis.com/customsearch/v1"
    
    def __init__(self, timeout: int = None, max_results: int = 10):
        super().__init__(
            timeout=timeout or settings.PROVIDER_TIMEOUT_GOOGLE,
            max_results=max_results
        )
        self.api_key = settings.GOOGLE_API_KEY
        self.cx = settings.GOOGLE_CX
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[SearchResult]:
        """Search using Google Custom Search API"""
        if not self.api_key or not self.cx:
            logger.warning("Google API credentials not configured")
            return []
        
        results = []
        start_index = offset + 1
        
        # Google API returns max 10 results per request
        while len(results) < limit:
            params = {
                "key": self.api_key,
                "cx": self.cx,
                "q": query,
                "start": start_index,
                "num": min(10, limit - len(results))
            }
            
            try:
                async with await create_session_with_retry() as session:
                    response = await session.get(
                        self.base_url,
                        params=params,
                        timeout=self.timeout
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    parsed = await self._parse_results(data, query)
                    results.extend(parsed)
                    
                    # Check if there are more results
                    if len(data.get("items", [])) < 10:
                        break
                    
                    start_index += 10
                    
            except httpx.TimeoutException:
                logger.error("Google search timeout", query=query)
                break
            except httpx.HTTPStatusError as e:
                logger.error("Google search error", status=e.response.status_code, error=str(e))
                break
            except Exception as e:
                logger.error("Google search failed", error=str(e))
                break
        
        return results[:limit]
    
    async def _parse_results(
        self,
        response_data: Dict[str, Any],
        query: str
    ) -> List[SearchResult]:
        """Parse Google API response"""
        results = []
        items = response_data.get("items", [])
        
        for idx, item in enumerate(items):
            try:
                result = SearchResult(
                    title=self._truncate_text(item.get("title", ""), 200),
                    url=self._sanitize_url(item.get("link", "")),
                    snippet=self._truncate_text(item.get("snippet", ""), 500),
                    source=self.name,
                    rank=idx,
                    relevance_score=0.0
                )
                results.append(result)
            except Exception as e:
                logger.warning("Failed to parse Google result", error=str(e))
                continue
        
        return results


class GoogleOrganicProvider(BaseProvider):
    """
    Google organic search (no API key required)
    Uses HTML scraping with anti-bot protection
    """
    
    name = "google_organic"
    base_url = "https://www.google.com/search"
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[SearchResult]:
        """Search Google organic results"""
        from anti_bot.request_session import create_anti_bot_session
        
        params = {
            "q": query,
            "num": limit,
            "start": offset,
            "hl": "en",
            "gl": "us"
        }
        
        results = []
        
        try:
            async with await create_anti_bot_session() as session:
                response = await session.get(
                    self.base_url,
                    params=params,
                    provider=self.name,
                    timeout=self.timeout
                )
                
                results = await self._parse_results(response.text, query)
                
        except Exception as e:
            logger.error("Google organic search failed", error=str(e))
        
        return results[:limit]
    
    async def _parse_results(
        self,
        response_text: str,
        query: str
    ) -> List[SearchResult]:
        """Parse Google HTML response"""
        results = []
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response_text, 'html.parser')
            
            # Find search result containers
            result_divs = soup.select('div.g') or soup.select('div.tF2Cxc')
            
            for idx, div in enumerate(result_divs[:self.max_results]):
                try:
                    # Extract title
                    title_elem = div.select_one('h3') or div.select_one('h3.LC20lb')
                    title = title_elem.get_text() if title_elem else ""
                    
                    # Extract URL
                    link_elem = div.select_one('a')
                    url = link_elem.get('href') if link_elem else ""
                    
                    # Extract snippet
                    snippet_elem = div.select_one('div.VwiC3b') or div.select_one('div.VwiC3b.MUxGbd')
                    snippet = snippet_elem.get_text() if snippet_elem else ""
                    
                    if title and url:
                        result = SearchResult(
                            title=self._truncate_text(title, 200),
                            url=self._sanitize_url(url),
                            snippet=self._truncate_text(snippet, 500),
                            source=self.name,
                            rank=idx
                        )
                        results.append(result)
                        
                except Exception as e:
                    logger.warning("Failed to parse Google result", error=str(e))
                    continue
                    
        except ImportError:
            logger.warning("BeautifulSoup not available for parsing")
        
        return results
