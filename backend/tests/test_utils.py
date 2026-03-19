"""
Tests for core utilities
"""
import pytest
from core.utils import (
    hash_query,
    sanitize_url,
    is_valid_url,
    extract_domain,
    normalize_text,
    truncate_text,
    calculate_relevance_score,
    format_search_result
)


def test_hash_query():
    """Test query hashing"""
    query = "test query"
    hash1 = hash_query(query)
    hash2 = hash_query(query)
    hash3 = hash_query("different query")
    
    assert hash1 == hash2
    assert hash1 != hash3
    assert len(hash1) == 64  # SHA256 hex length


def test_sanitize_url():
    """Test URL sanitization"""
    # Valid URLs
    assert sanitize_url("https://example.com") == "https://example.com"
    assert sanitize_url("http://example.com/path") == "http://example.com/path"
    
    # Invalid URLs
    assert sanitize_url("file:///etc/passwd") is None  # SSRF prevention
    assert sanitize_url("gopher://example.com") is None
    assert sanitize_url("not-a-url") is None
    assert sanitize_url("") is None


def test_is_valid_url():
    """Test URL validation"""
    assert is_valid_url("https://example.com") is True
    assert is_valid_url("file:///etc/passwd") is False
    assert is_valid_url("not-a-url") is False


def test_extract_domain():
    """Test domain extraction"""
    assert extract_domain("https://example.com/path") == "example.com"
    assert extract_domain("http://sub.example.com") == "sub.example.com"
    assert extract_domain("invalid") is None


def test_normalize_text():
    """Test text normalization"""
    assert normalize_text("  multiple   spaces  ") == "multiple spaces"
    assert normalize_text("special!@#$chars") == "specialchars"
    assert normalize_text("normal text") == "normal text"


def test_truncate_text():
    """Test text truncation"""
    assert truncate_text("short", 10) == "short"
    assert truncate_text("a" * 100, 10) == "a" * 7 + "..."
    assert truncate_text("", 10) == ""


def test_calculate_relevance_score():
    """Test relevance score calculation"""
    query = "python programming"
    
    # High relevance
    score1 = calculate_relevance_score(
        query,
        "Python Programming Guide",
        "Learn python programming here",
        rank=0
    )
    
    # Low relevance
    score2 = calculate_relevance_score(
        query,
        "Java Tutorial",
        "Learn java here",
        rank=0
    )
    
    assert score1 > score2
    assert 0 <= score1 <= 1
    assert 0 <= score2 <= 1


def test_format_search_result():
    """Test search result formatting"""
    result = format_search_result(
        title="Test Title",
        url="https://example.com",
        snippet="Test snippet",
        source="google",
        rank=1
    )
    
    assert result["title"] == "Test Title"
    assert result["url"] == "https://example.com"
    assert result["source"] == "google"
    assert result["rank"] == 1
    assert "timestamp" in result


def test_format_search_result_truncation():
    """Test search result truncation"""
    long_title = "a" * 300
    result = format_search_result(
        title=long_title,
        url="https://example.com",
        snippet="snippet",
        source="google",
        rank=1
    )
    
    assert len(result["title"]) <= 200
