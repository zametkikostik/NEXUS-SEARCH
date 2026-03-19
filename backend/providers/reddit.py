"""
Reddit Search Provider
"""
from typing import List, Dict, Any
import httpx
from core.config import get_settings
from core.logging import get_logger
from core.utils import create_session_with_retry
from providers.base import BaseProvider, SearchResult

settings = get_settings()
logger = get_logger(__name__)


class RedditProvider(BaseProvider):
    """Reddit search provider"""
    
    name = "reddit"
    base_url = "https://www.reddit.com/search/"
    api_url = "https://www.reddit.com/search.json"
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[SearchResult]:
        """Search Reddit"""
        from anti_bot.request_session import create_anti_bot_session
        
        params = {
            "q": query,
            "limit": min(limit, 25),
            "sort": "relevance"
        }
        
        results = []
        
        try:
            async with await create_anti_bot_session() as session:
                response = await session.get(
                    self.api_url,
                    params=params,
                    provider=self.name,
                    timeout=self.timeout,
                    headers={
                        "User-Agent": "NexusSearch/1.0"
                    }
                )
                
                data = response.json()
                results = await self._parse_results(data, query)
                
        except Exception as e:
            logger.error("Reddit search failed", error=str(e))
        
        return results[:limit]
    
    async def _parse_results(
        self,
        response_data: Dict[str, Any],
        query: str
    ) -> List[SearchResult]:
        """Parse Reddit JSON response"""
        results = []
        
        try:
            # Reddit returns children array
            children = response_data.get("data", {}).get("children", [])
            
            for idx, child in enumerate(children[:self.max_results]):
                try:
                    data = child.get("data", {})
                    
                    # Get post data
                    title = data.get("title", "")
                    subreddit = data.get("subreddit", "")
                    url = data.get("url", "")
                    selftext = data.get("selftext", "")
                    permalink = data.get("permalink", "")
                    
                    # Build full URL
                    if permalink and not url.startswith('http'):
                        full_url = f"https://www.reddit.com{permalink}"
                    else:
                        full_url = url if url else f"https://www.reddit.com{permalink}" if permalink else ""
                    
                    # Build snippet
                    snippet_parts = []
                    if subreddit:
                        snippet_parts.append(f"r/{subreddit}")
                    if selftext:
                        snippet_parts.append(selftext[:300])
                    snippet = " | ".join(snippet_parts)
                    
                    if title and full_url:
                        result = SearchResult(
                            title=self._truncate_text(title, 200),
                            url=self._sanitize_url(full_url),
                            snippet=self._truncate_text(snippet, 500),
                            source=self.name,
                            rank=idx
                        )
                        results.append(result)
                        
                except Exception as e:
                    logger.warning("Failed to parse Reddit result", error=str(e))
                    continue
                    
        except Exception as e:
            logger.error("Reddit parsing failed", error=str(e))
        
        return results


class RedditPostsProvider(BaseProvider):
    """Reddit posts search (specific subreddits)"""
    
    name = "reddit_posts"
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[SearchResult]:
        """Search Reddit posts in specific subreddits"""
        from anti_bot.request_session import create_anti_bot_session
        
        # Search in tech/crypto subreddits
        subreddits = ["technology", "crypto", "privacy", "web3", "decentralization"]
        results = []
        
        for subreddit in subreddits:
            if len(results) >= limit:
                break
                
            url = f"https://www.reddit.com/r/{subreddit}/search.json"
            params = {
                "q": query,
                "limit": 5,
                "sort": "relevance",
                "restrict_sr": True
            }
            
            try:
                async with await create_anti_bot_session() as session:
                    response = await session.get(
                        url,
                        params=params,
                        provider=self.name,
                        timeout=self.timeout,
                        headers={"User-Agent": "NexusSearch/1.0"}
                    )
                    
                    data = response.json()
                    children = data.get("data", {}).get("children", [])
                    
                    for child in children:
                        if len(results) >= limit:
                            break
                        
                        post_data = child.get("data", {})
                        title = post_data.get("title", "")
                        permalink = post_data.get("permalink", "")
                        selftext = post_data.get("selftext", "")
                        
                        if title and permalink:
                            result = SearchResult(
                                title=self._truncate_text(title, 200),
                                url=f"https://www.reddit.com{permalink}",
                                snippet=self._truncate_text(selftext[:200], 500),
                                source=f"r/{subreddit}",
                                rank=len(results)
                            )
                            results.append(result)
                            
            except Exception as e:
                logger.warning(f"Failed to search r/{subreddit}", error=str(e))
                continue
        
        return results
