import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_business_nodes_routes_exist():
    """测试业务节点路由存在"""
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # 测试获取列表路由（应该返回401，需要认证）
        response = await client.get("/api/business-nodes")
        assert response.status_code in [200, 401, 403]

        # 测试树状查询路由
        response = await client.get("/api/business-nodes/tree")
        assert response.status_code in [200, 401, 403]

        # 测试创建路由
        response = await client.post("/api/business-nodes", json={})
        assert response.status_code in [201, 401, 403, 422]
