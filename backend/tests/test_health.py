"""Basic tests to verify the app doesn't crash."""
import httpx
import pytest
import pytest_asyncio
from app.main import app


@pytest_asyncio.fixture
async def client():
    """Async test client for httpx 0.28+."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_api_status(client):
    response = await client.get("/api/v1/status/apis")
    assert response.status_code == 200
