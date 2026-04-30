import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_auth_routes_exist():
    """测试认证路由存在"""
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # 测试登录路由返回422（因为缺少数据，但证明路由存在）
        response = await client.post("/auth/login", json={})
        assert response.status_code in [200, 401, 422]

        # 测试refresh路由
        response = await client.post("/auth/refresh", json={})
        assert response.status_code in [200, 401, 422]

        # 测试me路由（需要认证）
        response = await client.get("/auth/me")
        assert response.status_code in [200, 401, 403]

