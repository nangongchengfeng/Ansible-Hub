"""
简单的网关功能测试
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base
from app.models.user import User
from app.models.system_user import SystemUser
from app.models.gateway import Gateway
from app.models.business_node import BusinessNode
from app.models.host import Host
from app.services.auth import AuthService
from app.services.system_user import SystemUserService
from app.services.gateway import GatewayService
from app.services.business_node import BusinessNodeService
from app.services.host import HostService


# 使用内存 SQLite 进行测试
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


async def test_gateway_delete_unbinds():
    """测试删除网关时自动解绑业务节点和主机"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # 创建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 创建会话
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        # 1. 创建用户
        user = await AuthService.create_user(
            session,
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_superuser=True
        )

        # 2. 创建系统用户
        system_user = await SystemUserService.create(
            session,
            name="test-sys",
            username="root",
            auth_type="password",
            password="test",
            created_by=user.id
        )

        # 3. 创建网关
        gateway = await GatewayService.create(
            session,
            gateway_in=type('', (), {
                'name': 'Test Gateway',
                'ip': '192.168.1.1',
                'port': 22,
                'system_user_id': system_user.id
            })(),
            created_by=user.id
        )

        # 4. 创建绑定网关的业务节点
        business_node = await BusinessNodeService.create(
            session,
            business_node_in=type('', (), {
                'name': 'Test Node',
                'description': None,
                'parent_id': None,
                'sort_order': 0,
                'gateway_id': gateway.id
            })(),
            created_by=user.id
        )

        # 5. 创建绑定网关的主机
        host = await HostService.create(
            session,
            host_in=type('', (), {
                'name': 'Test Host',
                'business_node_id': business_node.id,
                'ip_internal': '192.168.1.10',
                'ip_external': None,
                'ip_preference': 'internal',
                'ssh_port': 22,
                'cloud_provider': None,
                'system_user_id': system_user.id,
                'gateway_id': gateway.id
            })(),
            created_by=user.id
        )

        await session.commit()

        # 验证初始状态
        await session.refresh(business_node)
        await session.refresh(host)
        assert business_node.gateway_id == gateway.id
        assert host.gateway_id == gateway.id

        # 6. 删除网关
        await GatewayService.delete(session, gateway)

        # 7. 验证已解绑
        await session.refresh(business_node)
        await session.refresh(host)
        assert business_node.gateway_id is None
        assert host.gateway_id is None

        print("✓ 网关删除时自动解绑功能测试通过!")

    # 清理
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


async def test_gateway_creator_loaded():
    """测试网关详情正确加载 creator 信息"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # 创建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 创建会话
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        # 1. 创建用户
        user = await AuthService.create_user(
            session,
            username="creatoruser",
            email="creator@example.com",
            password="testpass123",
            is_superuser=True,
            real_name="Test Creator"
        )

        # 2. 创建系统用户
        system_user = await SystemUserService.create(
            session,
            name="test-sys",
            username="root",
            auth_type="password",
            password="test",
            created_by=user.id
        )

        # 3. 创建网关
        gateway = await GatewayService.create(
            session,
            gateway_in=type('', (), {
                'name': 'Creator Test Gateway',
                'ip': '192.168.1.1',
                'port': 22,
                'system_user_id': system_user.id
            })(),
            created_by=user.id
        )

        # 4. 获取网关详情
        gateway_detail = await GatewayService.get_by_id(session, gateway.id)

        # 验证 creator 已加载
        assert gateway_detail.creator is not None
        assert gateway_detail.creator.id == user.id
        assert gateway_detail.creator.username == "creatoruser"

        print("✓ 网关 creator 信息加载测试通过!")

    # 清理
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_gateway_delete_unbinds())
    print()
    asyncio.run(test_gateway_creator_loaded())
    print()
    print("✅ 所有简单测试通过!")
