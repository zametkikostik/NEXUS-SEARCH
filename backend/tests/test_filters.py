"""
Tests for content filters
"""
import pytest
from filters.blacklist import BlacklistFilter
from filters.ml_classifier import ContentClassifier
from filters.content_filter import ContentFilter


@pytest.fixture
def blacklist_filter():
    """Create blacklist filter"""
    filter = BlacklistFilter()
    filter.load()
    return filter


@pytest.fixture
def content_filter():
    """Create content filter"""
    filter = ContentFilter()
    filter.initialize()
    return filter


def test_blacklist_filter_extremism(blacklist_filter):
    """Test extremism detection"""
    text = "This extremist group promotes violence"
    result = blacklist_filter.check(text)
    
    assert result.get("extremism") is True


def test_blacklist_filter_clean(blacklist_filter):
    """Test clean text"""
    text = "This is a normal article about technology"
    result = blacklist_filter.check(text)
    
    assert not any(result.values())


def test_blacklist_filter_spam(blacklist_filter):
    """Test spam detection"""
    text = "Click here to buy now! Limited offer! Make money fast!"
    result = blacklist_filter.check(text)
    
    assert result.get("spam") is True


def test_blacklist_is_blocked(blacklist_filter):
    """Test is_blocked method"""
    assert blacklist_filter.is_blocked("extremist content here") is True
    assert blacklist_filter.is_blocked("normal content") is False


def test_blacklist_get_categories(blacklist_filter):
    """Test get_blocked_categories method"""
    text = "terrorist recruitment and bomb making instructions"
    categories = blacklist_filter.get_blocked_categories(text)
    
    assert "terrorism" in categories


def test_content_filter_combined(blacklist_filter):
    """Test combined content filter"""
    filter = ContentFilter()
    filter.initialize()
    
    # Blocked content
    result1 = filter.check("extremist propaganda content")
    assert result1["blocked"] is True
    
    # Clean content
    result2 = filter.check("normal technology news")
    assert result2["blocked"] is False


def test_filter_results(blacklist_filter):
    """Test filtering search results"""
    results = [
        {"title": "Normal Article", "snippet": "Technology news", "url": "https://example.com/1"},
        {"title": "Extremist Content", "snippet": "extremist propaganda", "url": "https://example.com/2"},
        {"title": "Another Article", "snippet": "More news", "url": "https://example.com/3"},
    ]
    
    filtered = blacklist_filter.filter_results(results)
    
    # Should remove blocked content
    assert len(filtered) < len(results)
    assert all(not r.get("filtered") for r in filtered)
