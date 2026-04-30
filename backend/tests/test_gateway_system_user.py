import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_gateway_and_system_user_routes_exist():
    """Test that gateway and system-user routes exist"""
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Test system-users routes
        response = await client.get("/api/system-users")
        assert response.status_code in [200, 401, 403]

        response = await client.post("/api/system-users", json={})
        assert response.status_code in [201, 401, 403, 422]

        response = await client.get("/api/system-users/1")
        assert response.status_code in [200, 401, 403, 404]

        response = await client.put("/api/system-users/1", json={})
        assert response.status_code in [200, 401, 403, 404, 422]

        response = await client.delete("/api/system-users/1")
        assert response.status_code in [200, 401, 403, 404]

        # Test gateways routes
        response = await client.get("/api/gateways")
        assert response.status_code in [200, 401, 403]

        response = await client.post("/api/gateways", json={})
        assert response.status_code in [201, 401, 403, 422]

        response = await client.get("/api/gateways/1")
        assert response.status_code in [200, 401, 403, 404]

        response = await client.put("/api/gateways/1", json={})
        assert response.status_code in [200, 401, 403, 404, 422]

        response = await client.delete("/api/gateways/1")
        assert response.status_code in [200, 401, 403, 404]
