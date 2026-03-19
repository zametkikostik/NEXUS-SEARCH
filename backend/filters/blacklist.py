"""
Blacklist-based Content Filter
"""
import re
from typing import List, Set, Dict, Optional
from pathlib import Path
from core.config import get_settings
from core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class BlacklistFilter:
    """Filter content based on keyword blacklists"""
    
    def __init__(self):
        self.blacklists: Dict[str, Set[str]] = {
            "extremism": set(),
            "terrorism": set(),
            "propaganda": set(),
            "adult": set(),
            "spam": set()
        }
        self._loaded = False
        self._patterns: Dict[str, List[re.Pattern]] = {}
    
    def load(self, blacklist_file: Optional[str] = None) -> None:
        """Load blacklists from file"""
        if self._loaded:
            return
        
        file_path = blacklist_file or settings.FILTER_BLACKLIST_FILE
        
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning("Blacklist file not found", file=file_path)
                self._load_default_blacklists()
                self._compile_patterns()
                self._loaded = True
                return
            
            with open(path, 'r', encoding='utf-8') as f:
                current_category = "general"
                
                for line in f:
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Category header
                    if line.startswith('[') and line.endswith(']'):
                        current_category = line[1:-1].lower()
                        if current_category not in self.blacklists:
                            self.blacklists[current_category] = set()
                        continue
                    
                    # Add keyword
                    if current_category in self.blacklists:
                        self.blacklists[current_category].add(line.lower())
            
            logger.info("Loaded blacklists", categories=list(self.blacklists.keys()))
            
        except Exception as e:
            logger.error("Failed to load blacklist", error=str(e))
            self._load_default_blacklists()
        
        self._compile_patterns()
        self._loaded = True
    
    def _load_default_blacklists(self) -> None:
        """Load default blacklist keywords"""
        # Extremism related
        self.blacklists["extremism"] = {
            "extremist", "extremism", "radicalize", "radicalization",
            "hate group", "supremacist", "white supremacy", "neo-nazi",
            "violent extremism", "domestic terrorism"
        }
        
        # Terrorism related
        self.blacklists["terrorism"] = {
            "terrorist", "terrorism", "jihadist", "militant group",
            "bomb making", "attack instructions", "recruitment for terrorism"
        }
        
        # Propaganda related
        self.blacklists["propaganda"] = {
            "state propaganda", "fake news", "disinformation campaign",
            "conspiracy theory", "election fraud claims", "anti-vaccine misinformation"
        }
        
        # Adult content
        self.blacklists["adult"] = {
            "porn", "xxx", "adult content", "explicit"
        }
        
        # Spam
        self.blacklists["spam"] = {
            "click here", "buy now", "limited offer", "act now",
            "free money", "work from home", "make money fast"
        }
        
        logger.info("Loaded default blacklists")
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for efficiency"""
        for category, keywords in self.blacklists.items():
            if keywords:
                # Create pattern that matches any keyword as whole word
                pattern_str = r'\b(' + '|'.join(re.escape(kw) for kw in keywords) + r')\b'
                self._patterns[category] = [re.compile(pattern_str, re.IGNORECASE)]
    
    def check(
        self,
        text: str,
        categories: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Check text against blacklists
        
        Returns:
            Dict mapping category to blocked status
        """
        if not self._loaded:
            self.load()
        
        if categories is None:
            categories = []
            if settings.BLOCK_EXTREMISM:
                categories.append("extremism")
            if settings.BLOCK_TERRORISM:
                categories.append("terrorism")
            if settings.BLOCK_PROPAGANDA:
                categories.append("propaganda")
            if settings.BLOCK_ADULT_CONTENT:
                categories.append("adult")
        
        results = {}
        text_lower = text.lower()
        
        for category in categories:
            if category in self._patterns:
                for pattern in self._patterns[category]:
                    if pattern.search(text_lower):
                        results[category] = True
                        break
                else:
                    results[category] = False
            else:
                results[category] = False
        
        return results
    
    def is_blocked(
        self,
        text: str,
        categories: Optional[List[str]] = None
    ) -> bool:
        """Check if text should be blocked"""
        results = self.check(text, categories)
        return any(results.values())
    
    def get_blocked_categories(
        self,
        text: str,
        categories: Optional[List[str]] = None
    ) -> List[str]:
        """Get list of blocked categories"""
        results = self.check(text, categories)
        return [cat for cat, blocked in results.items() if blocked]
    
    def filter_results(
        self,
        results: List[Dict],
        text_fields: List[str] = None
    ) -> List[Dict]:
        """Filter search results, removing blocked ones"""
        if not self._loaded:
            self.load()
        
        if text_fields is None:
            text_fields = ["title", "snippet"]
        
        filtered = []
        
        for result in results:
            # Combine text from all fields
            text_parts = []
            for field in text_fields:
                if field in result and result[field]:
                    text_parts.append(str(result[field]))
            
            combined_text = " ".join(text_parts)
            
            # Check if blocked
            if not self.is_blocked(combined_text):
                filtered.append(result)
            else:
                # Mark as filtered
                blocked_cats = self.get_blocked_categories(combined_text)
                result["filtered"] = True
                result["filter_reason"] = blocked_cats
        
        return filtered


# Global filter instance
blacklist_filter = BlacklistFilter()


def get_blacklist_filter() -> BlacklistFilter:
    """Get blacklist filter dependency"""
    if not blacklist_filter._loaded:
        blacklist_filter.load()
    return blacklist_filter
