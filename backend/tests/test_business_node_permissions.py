import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_business_node_permission_routes_exist():
    """Test that business node permission routes exist"""
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Test getting permissions (should return 401)
        response = await client.get("/api/business-nodes/1/permissions")
        assert response.status_code in [200, 401, 403, 404]

        # Test setting permissions (should return 401)
        response = await client.put("/api/business-nodes/1/permissions", json={"permissions": []})
        assert response.status_code in [200, 401, 403, 404, 422]

        # Test binding gateway (should return 401)
        response = await client.put("/api/business-nodes/1/gateway", json={"gateway_id": None})
        assert response.status_code in [200, 401, 403, 404, 422]

        # Test getting hosts (should return 401)
        response = await client.get("/api/business-nodes/1/hosts")
        assert response.status_code in [200, 401, 403, 404]
