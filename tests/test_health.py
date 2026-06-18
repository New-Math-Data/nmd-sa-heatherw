"""Tests for health check endpoints."""

from httpx import AsyncClient


async def test_health(client: AsyncClient) -> None:
    """GET /health returns 200 with healthy status."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


async def test_root(client: AsyncClient) -> None:
    """GET / returns 200 with root message."""
    response = await client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
