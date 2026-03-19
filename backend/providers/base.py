"""
Base Provider Interface
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time


@dataclass
class SearchResult:
    """Search result structure"""
    title: str
    url: str
    snippet: str
    source: str
    rank: int
    timestamp: float = None
    relevance_score: float = 0.0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "title": self.title[:200] if self.title else "",
            "url": self.url,
            "snippet": self.snippet[:500] if self.snippet else "",
            "source": self.source,
            "rank": self.rank,
            "timestamp": self.timestamp,
            "relevance_score": self.relevance_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResult":
        """Create from dictionary"""
        return cls(
            title=data.get("title", ""),
            url=data.get("url", ""),
            snippet=data.get("snippet", ""),
            source=data.get("source", ""),
            rank=data.get("rank", 0),
            timestamp=data.get("timestamp"),
            relevance_score=data.get("relevance_score", 0.0)
        )


class BaseProvider(ABC):
    """Abstract base class for search providers"""
    
    name: str = "base"
    base_url: str = ""
    
    def __init__(self, timeout: int = 10, max_results: int = 10):
        self.timeout = timeout
        self.max_results = max_results
    
    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[SearchResult]:
        """
        Perform search
        
        Args:
            query: Search query
            limit: Maximum number of results
            offset: Result offset for pagination
        
        Returns:
            List of SearchResult objects
        """
        pass
    
    @abstractmethod
    async def _parse_results(
        self,
        response_text: str,
        query: str
    ) -> List[SearchResult]:
        """Parse search results from response"""
        pass
    
    def _sanitize_url(self, url: str) -> str:
        """Sanitize URL"""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    def _truncate_text(self, text: str, max_length: int = 500) -> str:
        """Truncate text"""
        if not text:
            return ""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
    
    def _clean_html(self, html: str) -> str:
        """Remove HTML tags"""
        import re
        # Remove script and style elements
        html = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
        # Remove all other tags
        text = re.sub(r'<[^>]+>', '', html)
        # Normalize whitespace
        text = ' '.join(text.split())
        return text
    
    def is_enabled(self) -> bool:
        """Check if provider is enabled"""
        from core.config import get_settings
        settings = get_settings()
        
        enabled_map = {
            "google": settings.GOOGLE_ENABLED,
            "duckduckgo": settings.DUCKDUCKGO_ENABLED,
            "brave": settings.BRAVE_ENABLED,
            "yandex": settings.YANDEX_ENABLED,
            "dzen": settings.DZEN_ENABLED,
            "reddit": settings.REDDIT_ENABLED
        }
        
        return enabled_map.get(self.name.lower(), True)
    
    def get_timeout(self) -> int:
        """Get provider-specific timeout"""
        from core.config import get_settings
        settings = get_settings()
        
        timeout_map = {
            "google": settings.PROVIDER_TIMEOUT_GOOGLE,
            "duckduckgo": settings.PROVIDER_TIMEOUT_DUCKDUCKGO,
        }
        
        return timeout_map.get(self.name.lower(), settings.PROVIDER_TIMEOUT_DEFAULT)
