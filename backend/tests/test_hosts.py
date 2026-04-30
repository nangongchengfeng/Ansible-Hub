import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_hosts_routes_exist():
    """Test that host routes exist"""
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Test hosts routes
        response = await client.get("/api/hosts")
        assert response.status_code in [200, 401, 403]

        response = await client.post("/api/hosts", json={})
        assert response.status_code in [201, 401, 403, 422]

        response = await client.get("/api/hosts/1")
        assert response.status_code in [200, 401, 403, 404]

        response = await client.put("/api/hosts/1", json={})
        assert response.status_code in [200, 401, 403, 404, 422]

        response = await client.patch("/api/hosts/1/toggle", json={})
        assert response.status_code in [200, 401, 403, 404]

        response = await client.post("/api/hosts/1/move", json={})
        assert response.status_code in [200, 401, 403, 404, 422]

        response = await client.delete("/api/hosts/1")
        assert response.status_code in [200, 401, 403, 404]
