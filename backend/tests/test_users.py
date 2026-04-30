import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_users_routes_exist():
    """测试用户管理路由存在"""
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # 测试需要认证
        response = await client.get("/users")
        assert response.status_code in [200, 401, 403]
