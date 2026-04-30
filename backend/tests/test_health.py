import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_health_check():
    """测试健康检查端点正常工作"""
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
