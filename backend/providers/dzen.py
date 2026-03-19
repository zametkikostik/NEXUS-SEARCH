"""
Dzen Search Provider
"""
from typing import List, Dict, Any
import httpx
from core.config import get_settings
from core.logging import get_logger
from core.utils import create_session_with_retry
from providers.base import BaseProvider, SearchResult

settings = get_settings()
logger = get_logger(__name__)


class DzenProvider(BaseProvider):
    """Dzen (Yandex Zen) content search provider"""
    
    name = "dzen"
    base_url = "https://dzen.ru/search"
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[SearchResult]:
        """Search Dzen content"""
        from anti_bot.request_session import create_anti_bot_session
        
        params = {
            "q": query,
            "offset": offset
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
            logger.error("Dzen search failed", error=str(e))
        
        return results[:limit]
    
    async def _parse_results(
        self,
        response_text: str,
        query: str
    ) -> List[SearchResult]:
        """Parse Dzen HTML response"""
        results = []
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response_text, 'html.parser')
            
            # Find article cards
            article_divs = soup.select('a.Link.Card')
            
            for idx, div in enumerate(article_divs[:self.max_results]):
                try:
                    # Extract title
                    title_elem = div.select_one('div.CardTitle')
                    title = title_elem.get_text() if title_elem else ""
                    
                    # Extract URL
                    url = div.get('href') if div else ""
                    if url and url.startswith('/'):
                        url = f"https://dzen.ru{url}"
                    
                    # Extract snippet/description
                    snippet_elem = div.select_one('div.CardDescription')
                    snippet = snippet_elem.get_text() if snippet_elem else ""
                    
                    # Extract author
                    author_elem = div.select_one('div.CardAuthor')
                    author = author_elem.get_text() if author_elem else ""
                    
                    if title and url:
                        snippet_with_author = f"{author}: {snippet}" if author else snippet
                        result = SearchResult(
                            title=self._truncate_text(title, 200),
                            url=self._sanitize_url(url),
                            snippet=self._truncate_text(snippet_with_author, 500),
                            source=self.name,
                            rank=idx
                        )
                        results.append(result)
                        
                except Exception as e:
                    logger.warning("Failed to parse Dzen result", error=str(e))
                    continue
                    
        except ImportError:
            logger.warning("BeautifulSoup not available for Dzen parsing")
        except Exception as e:
            logger.error("Dzen parsing failed", error=str(e))
        
        return results
