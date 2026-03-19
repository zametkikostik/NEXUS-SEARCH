"""
DuckDuckGo Search Provider
"""
import json
import re
from typing import List, Dict, Any
import httpx
from core.config import get_settings
from core.logging import get_logger
from core.utils import create_session_with_retry
from providers.base import BaseProvider, SearchResult

settings = get_settings()
logger = get_logger(__name__)


class DuckDuckGoProvider(BaseProvider):
    """DuckDuckGo search provider (HTML scraping)"""
    
    name = "duckduckgo"
    base_url = "https://html.duckduckgo.com/html/"
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[SearchResult]:
        """Search DuckDuckGo"""
        from anti_bot.request_session import create_anti_bot_session
        
        data = {"q": query}
        results = []
        
        try:
            async with await create_anti_bot_session() as session:
                response = await session.post(
                    self.base_url,
                    data=data,
                    provider=self.name,
                    timeout=self.timeout,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                results = await self._parse_results(response.text, query)
                
        except Exception as e:
            logger.error("DuckDuckGo search failed", error=str(e))
        
        return results[:limit]
    
    async def _parse_results(
        self,
        response_text: str,
        query: str
    ) -> List[SearchResult]:
        """Parse DuckDuckGo HTML response"""
        results = []
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response_text, 'html.parser')
            
            # Find result containers
            result_divs = soup.select('div.results_links_deep')
            
            for idx, div in enumerate(result_divs[:self.max_results]):
                try:
                    # Extract title
                    title_elem = div.select_one('a.result__title')
                    title = title_elem.get_text() if title_elem else ""
                    
                    # Extract URL
                    link_elem = div.select_one('a.result__url')
                    url = link_elem.get('href') if link_elem else ""
                    
                    # DuckDuckGo uses special URL encoding
                    if url and url.startswith('//'):
                        url = 'https:' + url
                    
                    # Extract snippet
                    snippet_elem = div.select_one('a.result__snippet')
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
                    logger.warning("Failed to parse DuckDuckGo result", error=str(e))
                    continue
                    
        except ImportError:
            # Fallback: regex-based parsing
            results = self._regex_parse(response_text, query)
        
        return results
    
    def _regex_parse(self, html: str, query: str) -> List[SearchResult]:
        """Fallback regex parsing"""
        results = []
        
        # Match result blocks
        pattern = r'<a[^>]+class="result__title"[^>]*>(.*?)</a>'
        matches = re.findall(pattern, html, re.DOTALL)
        
        for idx, match in enumerate(matches[:self.max_results]):
            try:
                # Extract title text
                title = re.sub(r'<[^>]+>', '', match).strip()
                
                # Extract URL from href
                url_match = re.search(r'href="([^"]+)"', match)
                url = url_match.group(1) if url_match else ""
                
                if title and url:
                    results.append(SearchResult(
                        title=self._truncate_text(title, 200),
                        url=self._sanitize_url(url),
                        snippet="",
                        source=self.name,
                        rank=idx
                    ))
            except Exception:
                continue
        
        return results


class DuckDuckGoAPIProvider(BaseProvider):
    """
    DuckDuckGo Instant Answer API
    Limited but doesn't require API key
    """
    
    name = "duckduckgo_api"
    base_url = "https://api.duckduckgo.com/"
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[SearchResult]:
        """Search using DuckDuckGo API"""
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
        
        results = []
        
        try:
            async with await create_session_with_retry() as session:
                response = await session.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
                
                results = await self._parse_results(data, query)
                
        except Exception as e:
            logger.error("DuckDuckGo API search failed", error=str(e))
        
        return results[:limit]
    
    async def _parse_results(
        self,
        response_data: Dict[str, Any],
        query: str
    ) -> List[SearchResult]:
        """Parse DuckDuckGo API response"""
        results = []
        
        # Extract abstract
        abstract = response_data.get("Abstract", "")
        abstract_url = response_data.get("AbstractURL", "")
        abstract_source = response_data.get("AbstractSource", "")
        
        if abstract and abstract_url:
            results.append(SearchResult(
                title=self._truncate_text(abstract_source or "DuckDuckGo", 200),
                url=self._sanitize_url(abstract_url),
                snippet=self._truncate_text(abstract, 500),
                source=self.name,
                rank=0
            ))
        
        # Extract related topics
        related = response_data.get("RelatedTopics", [])
        for idx, topic in enumerate(related[:self.max_results], start=1):
            try:
                if isinstance(topic, dict) and "Text" in topic:
                    text = topic.get("Text", "")
                    first_url = topic.get("FirstURL", "")
                    
                    if text and first_url:
                        results.append(SearchResult(
                            title=self._truncate_text(text.split(" - ")[0], 200),
                            url=self._sanitize_url(first_url),
                            snippet=self._truncate_text(text, 500),
                            source=self.name,
                            rank=idx
                        ))
            except Exception:
                continue
        
        return results
