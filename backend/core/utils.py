"""
Core Utilities
"""
import hashlib
import time
import re
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse
import aiohttp
import httpx


def hash_query(query: str) -> str:
    """Create hash of search query for caching"""
    normalized = query.lower().strip()
    return hashlib.sha256(normalized.encode()).hexdigest()


def sanitize_url(url: str) -> Optional[str]:
    """Sanitize and validate URL"""
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return None
        
        # Prevent SSRF
        blocked_schemes = {'file', 'gopher', 'dict', 'ftp'}
        if parsed.scheme.lower() in blocked_schemes:
            return None
        
        # Only allow http/https
        if parsed.scheme.lower() not in ('http', 'https'):
            return None
        
        return url
    except Exception:
        return None


def is_valid_url(url: str) -> bool:
    """Check if URL is valid"""
    return sanitize_url(url) is not None


def extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None


def normalize_text(text: str) -> str:
    """Normalize text for processing"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters
    text = re.sub(r'[^\w\s\-\.\,]', '', text)
    return text.strip()


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def calculate_relevance_score(
    query: str,
    title: str,
    snippet: str,
    rank: int = 0
) -> float:
    """Calculate relevance score for search result"""
    query_terms = query.lower().split()
    title_lower = title.lower()
    snippet_lower = snippet.lower()
    
    score = 0.0
    
    # Title matches (higher weight)
    for term in query_terms:
        if term in title_lower:
            score += 0.3
    
    # Snippet matches
    for term in query_terms:
        if term in snippet_lower:
            score += 0.1
    
    # Rank bonus (lower rank = higher bonus)
    rank_bonus = max(0, (1.0 - (rank / 50))) * 0.2
    score += rank_bonus
    
    return min(score, 1.0)


class RequestTimeout:
    """Context manager for request timeout"""
    
    def __init__(self, seconds: float):
        self.seconds = seconds
    
    async def __aenter__(self):
        self.start_time = time.monotonic()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.monotonic() - self.start_time
        if elapsed > self.seconds:
            raise asyncio.TimeoutError(f"Request exceeded {self.seconds}s timeout")


async def create_session_with_retry(
    max_retries: int = 3,
    backoff_factor: float = 1.5,
    timeout: int = 30
) -> httpx.AsyncClient:
    """Create HTTPX session with retry configuration"""
    timeout_config = httpx.Timeout(timeout=timeout, connect=10.0)
    limits = httpx.Limits(max_keepalive_connections=20, max_connections=50)
    
    return httpx.AsyncClient(
        timeout=timeout_config,
        limits=limits,
        headers={
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
    )


def get_random_user_agent() -> str:
    """Get random User-Agent string"""
    user_agents = [
        # Chrome
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Firefox
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        # Safari
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        # Edge
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    ]
    import random
    return random.choice(user_agents)


def parse_proxy_string(proxy: str) -> Dict[str, str]:
    """Parse proxy string to dict"""
    # Formats: host:port, user:pass@host:port, http://host:port
    proxy_dict = {"http": proxy, "https": proxy}
    return proxy_dict


def merge_results(
    results: List[Dict[str, Any]],
    query: str
) -> List[Dict[str, Any]]:
    """Merge and deduplicate search results"""
    seen_urls = set()
    merged = []
    
    for idx, result in enumerate(results):
        url = result.get("url", "")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        
        # Calculate relevance
        result["relevance_score"] = calculate_relevance_score(
            query,
            result.get("title", ""),
            result.get("snippet", ""),
            result.get("rank", idx)
        )
        
        merged.append(result)
    
    # Sort by relevance
    merged.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    return merged


def format_search_result(
    title: str,
    url: str,
    snippet: str,
    source: str,
    rank: int = 0
) -> Dict[str, Any]:
    """Format search result to standard schema"""
    return {
        "title": truncate_text(title, 200),
        "url": sanitize_url(url) or "",
        "snippet": truncate_text(snippet, 500),
        "source": source,
        "rank": rank,
        "timestamp": time.time()
    }
