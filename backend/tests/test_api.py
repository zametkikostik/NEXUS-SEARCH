"""
Tests for NEXUS Search Backend
"""
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from api.main import app


@pytest.fixture
async def client():
    """Create async test client"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_root(client):
    """Test root endpoint"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "NEXUS Search"
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_liveness_check(client):
    """Test liveness endpoint"""
    response = await client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_search_empty_query(client):
    """Test search with empty query"""
    response = await client.get("/api/v1/search?q=")
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_search_basic(client):
    """Test basic search"""
    response = await client.get("/api/v1/search?q=test")
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "results" in data
    assert data["query"] == "test"


@pytest.mark.asyncio
async def test_search_with_limit(client):
    """Test search with limit parameter"""
    response = await client.get("/api/v1/search?q=test&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) <= 5


@pytest.mark.asyncio
async def test_providers_endpoint(client):
    """Test providers endpoint"""
    response = await client.get("/api/v1/search/providers")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data


@pytest.mark.asyncio
async def test_auth_message(client):
    """Test auth message generation"""
    test_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
    response = await client.get(f"/api/v1/auth/message?address={test_address}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "address" in data


@pytest.mark.asyncio
async def test_auth_verify_invalid_signature(client):
    """Test auth verification with invalid signature"""
    test_data = {
        "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "message": "test message",
        "signature": "0xinvalid"
    }
    response = await client.post("/api/v1/auth/verify", json=test_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_ipfs_stats(client):
    """Test IPFS stats endpoint"""
    response = await client.get("/api/v1/ipfs/stats")
    assert response.status_code == 200
    data = response.json()
    assert "connected" in data


@pytest.mark.asyncio
async def test_rate_limit_info(client):
    """Test rate limit endpoint"""
    response = await client.get("/api/v1/auth/rate-limit")
    assert response.status_code == 200
    data = response.json()
    assert "limit" in data
    assert "remaining" in data


@pytest.mark.asyncio
async def test_search_validation(client):
    """Test search query validation"""
    # Too long query
    long_query = "a" * 501
    response = await client.get(f"/api/v1/search?q={long_query}")
    assert response.status_code == 422
    
    # Invalid limit
    response = await client.get("/api/v1/search?q=test&limit=100")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_cors_headers(client):
    """Test CORS headers"""
    response = await client.get(
        "/",
        headers={"Origin": "http://localhost:3000"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_api_version(client):
    """Test API version in paths"""
    response = await client.get("/api/v1/health")
    assert response.status_code == 404  # Health is not under /api/v1
    
    response = await client.get("/health")
    assert response.status_code == 200
