import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.services.auth import AuthService
from app.services.system_user import SystemUserService
from app.services.gateway import GatewayService
from app.services.business_node import BusinessNodeService
from app.services.host import HostService


@pytest.fixture
def auth_headers():
    """获取认证头的fixture"""
    return {}


@pytest.mark.asyncio
async def test_gateway_crud_flow(db_session: AsyncSession):
    """测试网关完整的 CRUD 流程"""
    # 1. 创建测试用户并登录获取 token
    await AuthService.create_user(
        db_session,
        username="testadmin",
        email="testadmin@example.com",
        password="testpass123",
        is_superuser=True
    )

    # 2. 创建系统用户
    system_user = await SystemUserService.create(
        db_session,
        name="test-system-user",
        username="root",
        auth_type="password",
        password="testpass",
        created_by=1
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # 先登录获取 token
        login_response = await client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "testpass123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # 3. 创建网关
        create_response = await client.post(
            "/api/gateways",
            json={
                "name": "测试网关",
                "ip": "192.168.1.100",
                "port": 22,
                "system_user_id": system_user.id
            },
            headers=auth_headers
        )
        assert create_response.status_code == 201
        gateway_data = create_response.json()
        assert gateway_data["name"] == "测试网关"
        assert gateway_data["ip"] == "192.168.1.100"
        gateway_id = gateway_data["id"]

        # 4. 获取网关列表
        list_response = await client.get("/api/gateways", headers=auth_headers)
        assert list_response.status_code == 200
        gateways = list_response.json()
        assert len(gateways) >= 1

        # 5. 获取网关详情
        detail_response = await client.get(f"/api/gateways/{gateway_id}", headers=auth_headers)
        assert detail_response.status_code == 200
        detail_data = detail_response.json()
        assert detail_data["id"] == gateway_id
        assert detail_data["name"] == "测试网关"
        assert "system_user" in detail_data
        assert "created_by" in detail_data

        # 6. 更新网关
        update_response = await client.put(
            f"/api/gateways/{gateway_id}",
            json={"name": "更新后的网关", "port": 2222},
            headers=auth_headers
        )
        assert update_response.status_code == 200
        updated_data = update_response.json()
        assert updated_data["name"] == "更新后的网关"
        assert updated_data["port"] == 2222

        # 7. 删除网关
        delete_response = await client.delete(
            f"/api/gateways/{gateway_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 204

        # 8. 验证网关已删除
        get_deleted_response = await client.get(
            f"/api/gateways/{gateway_id}",
            headers=auth_headers
        )
        assert get_deleted_response.status_code == 404


@pytest.mark.asyncio
async def test_gateway_search(db_session: AsyncSession):
    """测试网关搜索功能"""
    # 创建测试用户
    await AuthService.create_user(
        db_session,
        username="searchuser",
        email="searchuser@example.com",
        password="testpass123",
        is_superuser=True
    )

    # 创建系统用户
    system_user = await SystemUserService.create(
        db_session,
        name="search-sys-user",
        username="root",
        auth_type="password",
        password="testpass",
        created_by=1
    )

    # 创建多个网关
    await GatewayService.create(
        db_session,
        gateway_in=type('', (), {
            'name': '生产网关',
            'ip': '192.168.1.1',
            'port': 22,
            'system_user_id': system_user.id
        })(),
        created_by=1
    )
    await GatewayService.create(
        db_session,
        gateway_in=type('', (), {
            'name': '测试网关',
            'ip': '192.168.1.2',
            'port': 22,
            'system_user_id': system_user.id
        })(),
        created_by=1
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # 登录
        login_response = await client.post(
            "/api/auth/login",
            json={"username": "searchuser", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # 测试按名称搜索
        search_response = await client.get(
            "/api/gateways?search=生产",
            headers=auth_headers
        )
        assert search_response.status_code == 200
        results = search_response.json()
        assert len(results) == 1
        assert results[0]["name"] == "生产网关"

        # 测试按 IP 搜索
        search_response = await client.get(
            "/api/gateways?search=192.168.1.2",
            headers=auth_headers
        )
        assert search_response.status_code == 200
        results = search_response.json()
        assert len(results) == 1
        assert results[0]["ip"] == "192.168.1.2"


@pytest.mark.asyncio
async def test_gateway_delete_unbinds_business_nodes_and_hosts(db_session: AsyncSession):
    """测试删除网关时自动解绑业务节点和主机"""
    # 创建测试用户
    await AuthService.create_user(
        db_session,
        username="unbinduser",
        email="unbinduser@example.com",
        password="testpass123",
        is_superuser=True
    )

    # 创建系统用户
    system_user = await SystemUserService.create(
        db_session,
        name="unbind-sys-user",
        username="root",
        auth_type="password",
        password="testpass",
        created_by=1
    )

    # 创建网关
    gateway = await GatewayService.create(
        db_session,
        gateway_in=type('', (), {
            'name': '待删除网关',
            'ip': '192.168.1.100',
            'port': 22,
            'system_user_id': system_user.id
        })(),
        created_by=1
    )

    # 创建绑定网关的业务节点
    business_node = await BusinessNodeService.create(
        db_session,
        business_node_in=type('', (), {
            'name': '测试业务节点',
            'description': None,
            'parent_id': None,
            'sort_order': 0,
            'gateway_id': gateway.id
        })(),
        created_by=1
    )
    assert business_node.gateway_id == gateway.id

    # 创建绑定网关的主机
    host = await HostService.create(
        db_session,
        host_in=type('', (), {
            'name': '测试主机',
            'business_node_id': business_node.id,
            'ip_internal': '192.168.1.10',
            'ip_external': None,
            'ip_preference': 'internal',
            'ssh_port': 22,
            'cloud_provider': None,
            'system_user_id': system_user.id,
            'gateway_id': gateway.id
        })(),
        created_by=1
    )
    assert host.gateway_id == gateway.id

    await db_session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # 登录
        login_response = await client.post(
            "/api/auth/login",
            json={"username": "unbinduser", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # 删除网关
        delete_response = await client.delete(
            f"/api/gateways/{gateway.id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 204

    # 验证业务节点和主机的 gateway_id 已被设为 null
    await db_session.refresh(business_node)
    await db_session.refresh(host)
    assert business_node.gateway_id is None
    assert host.gateway_id is None


@pytest.mark.asyncio
async def test_gateway_permissions(db_session: AsyncSession):
    """测试网关权限控制"""
    # 创建普通用户和管理员用户
    await AuthService.create_user(
        db_session,
        username="adminuser",
        email="admin@example.com",
        password="testpass123",
        is_superuser=True
    )
    await AuthService.create_user(
        db_session,
        username="normaluser",
        email="normal@example.com",
        password="testpass123",
        is_superuser=False,
        role="operator"
    )

    # 创建系统用户
    system_user = await SystemUserService.create(
        db_session,
        name="perm-sys-user",
        username="root",
        auth_type="password",
        password="testpass",
        created_by=1
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # 普通用户登录 - 不能创建网关
        normal_login = await client.post(
            "/api/auth/login",
            json={"username": "normaluser", "password": "testpass123"}
        )
        normal_token = normal_login.json()["access_token"]
        normal_headers = {"Authorization": f"Bearer {normal_token}"}

        create_response = await client.post(
            "/api/gateways",
            json={
                "name": "测试",
                "ip": "1.1.1.1",
                "port": 22,
                "system_user_id": system_user.id
            },
            headers=normal_headers
        )
        assert create_response.status_code == 403

        # 管理员用户登录 - 可以创建网关
        admin_login = await client.post(
            "/api/auth/login",
            json={"username": "adminuser", "password": "testpass123"}
        )
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        create_response = await client.post(
            "/api/gateways",
            json={
                "name": "权限测试网关",
                "ip": "192.168.1.1",
                "port": 22,
                "system_user_id": system_user.id
            },
            headers=admin_headers
        )
        assert create_response.status_code == 201
        gateway_id = create_response.json()["id"]

        # 普通用户可以查看网关
        get_response = await client.get(
            f"/api/gateways/{gateway_id}",
            headers=normal_headers
        )
        assert get_response.status_code == 200

        # 普通用户不能更新网关
        update_response = await client.put(
            f"/api/gateways/{gateway_id}",
            json={"name": "被修改的网关"},
            headers=normal_headers
        )
        assert update_response.status_code == 403

        # 普通用户不能删除网关
        delete_response = await client.delete(
            f"/api/gateways/{gateway_id}",
            headers=normal_headers
        )
        assert delete_response.status_code == 403


@pytest.mark.asyncio
async def test_gateway_validation(db_session: AsyncSession):
    """测试网关数据验证"""
    # 创建测试用户
    await AuthService.create_user(
        db_session,
        username="validuser",
        email="validuser@example.com",
        password="testpass123",
        is_superuser=True
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # 登录
        login_response = await client.post(
            "/api/auth/login",
            json={"username": "validuser", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # 测试无效的端口号
        create_response = await client.post(
            "/api/gateways",
            json={
                "name": "测试网关",
                "ip": "192.168.1.1",
                "port": 99999,  # 无效端口
                "system_user_id": 999  # 不存在的系统用户
            },
            headers=auth_headers
        )
        assert create_response.status_code == 422  # 验证错误

        # 测试使用不存在的系统用户
        create_response = await client.post(
            "/api/gateways",
            json={
                "name": "测试网关",
                "ip": "192.168.1.1",
                "port": 22,
                "system_user_id": 9999  # 不存在
            },
            headers=auth_headers
        )
        assert create_response.status_code == 404
