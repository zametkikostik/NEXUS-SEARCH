"""
Combined Content Filter - uses both blacklist and ML classifier
"""
from typing import List, Dict, Optional
from core.config import get_settings
from core.logging import get_logger
from core.exceptions import ContentFilterException
from filters.blacklist import BlacklistFilter, get_blacklist_filter
from filters.ml_classifier import ContentClassifier, get_content_classifier

settings = get_settings()
logger = get_logger(__name__)


class ContentFilter:
    """Combined content filtering system"""
    
    def __init__(self):
        self.blacklist: Optional[BlacklistFilter] = None
        self.classifier: Optional[ContentClassifier] = None
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize filters"""
        if self._initialized:
            return
        
        if settings.FILTER_ENABLED:
            self.blacklist = get_blacklist_filter()
            self.classifier = get_content_classifier()
            logger.info("Content filters initialized")
        
        self._initialized = True
    
    def check(self, text: str) -> Dict:
        """
        Check content against all filters
        
        Returns:
            Dict with filter results
        """
        if not self._initialized:
            self.initialize()
        
        if not settings.FILTER_ENABLED:
            return {"blocked": False, "reasons": []}
        
        reasons = []
        scores = {}
        
        # Blacklist check
        if self.blacklist:
            blocked_cats = self.blacklist.get_blocked_categories(text)
            if blocked_cats:
                reasons.extend(blocked_cats)
                scores["blacklist"] = {cat: True for cat in blocked_cats}
        
        # ML classification
        if self.classifier:
            classification = self.classifier.classify(text)
            if classification.is_blocked:
                if classification.category not in reasons:
                    reasons.append(classification.category)
                scores["ml"] = {
                    "category": classification.category,
                    "confidence": classification.confidence
                }
        
        return {
            "blocked": len(reasons) > 0,
            "reasons": reasons,
            "scores": scores
        }
    
    def filter_results(
        self,
        results: List[Dict],
        text_fields: List[str] = None
    ) -> List[Dict]:
        """
        Filter search results
        
        Args:
            results: List of search result dicts
            text_fields: Fields to check (default: title, snippet)
        
        Returns:
            Filtered results
        """
        if not self._initialized:
            self.initialize()
        
        if not settings.FILTER_ENABLED:
            return results
        
        if text_fields is None:
            text_fields = ["title", "snippet"]
        
        filtered = []
        filter_stats = {"total": len(results), "blocked": 0, "passed": 0}
        
        for result in results:
            # Combine text from all fields
            text_parts = []
            for field in text_fields:
                if field in result and result[field]:
                    text_parts.append(str(result[field]))
            
            combined_text = " ".join(text_parts)
            
            # Check content
            check_result = self.check(combined_text)
            
            if not check_result["blocked"]:
                filtered.append(result)
                filter_stats["passed"] += 1
            else:
                filter_stats["blocked"] += 1
                logger.debug(
                    "Content filtered",
                    reasons=check_result["reasons"],
                    url=result.get("url", "")
                )
        
        logger.info(
            "Content filtering complete",
            **filter_stats
        )
        
        return filtered
    
    def should_block_url(self, url: str) -> bool:
        """Check if URL domain should be blocked"""
        if not self._initialized:
            self.initialize()
        
        if not settings.FILTER_ENABLED or not self.blacklist:
            return False
        
        # Extract domain
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.lower()
            
            # Check against known bad domains
            bad_domains = [
                "extremist-site.com",
                "terror-content.org",
                "propaganda-network.net"
            ]
            
            return any(bad in domain for bad in bad_domains)
            
        except Exception:
            return False


# Global filter instance
content_filter = ContentFilter()


def get_content_filter() -> ContentFilter:
    """Get content filter dependency"""
    if not content_filter._initialized:
        content_filter.initialize()
    return content_filter
