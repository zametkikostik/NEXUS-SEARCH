"""
Yandex Search Provider
"""
from typing import List, Dict, Any
import httpx
from core.config import get_settings
from core.logging import get_logger
from core.utils import create_session_with_retry
from providers.base import BaseProvider, SearchResult

settings = get_settings()
logger = get_logger(__name__)


class YandexProvider(BaseProvider):
    """Yandex Search API provider"""
    
    name = "yandex"
    base_url = "https://yandex.com/search/"
    
    def __init__(self, timeout: int = 10, max_results: int = 10):
        super().__init__(timeout=timeout, max_results=max_results)
        self.api_key = settings.YANDEX_API_KEY
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[SearchResult]:
        """Search Yandex (HTML scraping)"""
        from anti_bot.request_session import create_anti_bot_session
        
        params = {
            "text": query,
            "lr": 213,  # Moscow region
            "lang": "en"
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
            logger.error("Yandex search failed", error=str(e))
        
        return results[:limit]
    
    async def _parse_results(
        self,
        response_text: str,
        query: str
    ) -> List[SearchResult]:
        """Parse Yandex HTML response"""
        results = []
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response_text, 'html.parser')
            
            # Find result containers
            result_divs = soup.select('li.serp-item')
            
            for idx, div in enumerate(result_divs[:self.max_results]):
                try:
                    # Extract title
                    title_elem = div.select_one('a.Link.OrganicTitle')
                    title = title_elem.get_text() if title_elem else ""
                    
                    # Extract URL
                    link_elem = div.select_one('a.Link.OrganicTitle')
                    url = link_elem.get('href') if link_elem else ""
                    
                    # Extract snippet
                    snippet_elem = div.select_one('div.OrganicText')
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
                    logger.warning("Failed to parse Yandex result", error=str(e))
                    continue
                    
        except ImportError:
            logger.warning("BeautifulSoup not available for Yandex parsing")
        except Exception as e:
            logger.error("Yandex parsing failed", error=str(e))
        
        return results
