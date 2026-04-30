from typing import Optional, List, Tuple
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.gateway import Gateway
from app.schemas.gateway import GatewayCreate, GatewayUpdate


class GatewayService:
    """网关服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, gateway_id: int) -> Optional[Gateway]:
        """通过ID获取网关"""
        result = await db.execute(
            select(Gateway)
            .where(Gateway.id == gateway_id)
            .options(selectinload(Gateway.system_user))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> Tuple[int, List[Gateway]]:
        """获取网关列表"""
        # Build conditions
        conditions = []
        if search:
            conditions.append(
                or_(
                    Gateway.name.contains(search),
                    Gateway.ip.contains(search)
                )
            )

        # Count
        count_query = select(Gateway.id)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # Query data
        data_query = select(Gateway).options(selectinload(Gateway.system_user))
        if conditions:
            data_query = data_query.where(and_(*conditions))
        data_query = data_query.order_by(Gateway.created_at.desc()).offset(skip).limit(limit)
        data_result = await db.execute(data_query)
        gateways = list(data_result.scalars().all())

        return total, gateways

    @staticmethod
    async def create(
        db: AsyncSession,
        gateway_in: GatewayCreate,
        created_by: int,
    ) -> Gateway:
        """创建网关"""
        gateway = Gateway(
            name=gateway_in.name,
            ip=gateway_in.ip,
            port=gateway_in.port,
            system_user_id=gateway_in.system_user_id,
            created_by=created_by,
        )
        db.add(gateway)
        await db.commit()
        await db.refresh(gateway)
        # Load system_user relationship
        await db.execute(select(Gateway).where(Gateway.id == gateway.id).options(selectinload(Gateway.system_user)))
        return gateway

    @staticmethod
    async def update(
        db: AsyncSession,
        gateway: Gateway,
        gateway_in: GatewayUpdate,
    ) -> Gateway:
        """更新网关"""
        update_data = gateway_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(gateway, field, value)

        await db.commit()
        await db.refresh(gateway)
        # Load system_user relationship
        await db.execute(select(Gateway).where(Gateway.id == gateway.id).options(selectinload(Gateway.system_user)))
        return gateway

    @staticmethod
    async def delete(db: AsyncSession, gateway: Gateway):
        """删除网关（自动解绑业务节点和主机）"""
        # TODO: Unbind from business_nodes and hosts (set gateway_id to null)
        await db.delete(gateway)
        await db.commit()
