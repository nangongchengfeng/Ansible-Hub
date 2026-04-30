from typing import Optional, List, Tuple
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.business_node import BusinessNode
from app.schemas.business_node import BusinessNodeCreate, BusinessNodeUpdate


class BusinessNodeService:
    """业务节点服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, node_id: int) -> Optional[BusinessNode]:
        """通过ID获取业务节点"""
        result = await db.execute(select(BusinessNode).where(BusinessNode.id == node_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        parent_id: Optional[int] = None,
    ) -> Tuple[int, List[BusinessNode]]:
        """获取业务节点列表"""
        # 构建查询条件
        conditions = []
        if parent_id is not None:
            conditions.append(BusinessNode.parent_id == parent_id)

        # 查询总数
        count_query = select(BusinessNode.id)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # 查询数据
        data_query = select(BusinessNode)
        if conditions:
            data_query = data_query.where(and_(*conditions))
        data_query = data_query.order_by(BusinessNode.sort_order, BusinessNode.id).offset(skip).limit(limit)
        data_result = await db.execute(data_query)
        nodes = list(data_result.scalars().all())

        return total, nodes

    @staticmethod
    async def get_tree(db: AsyncSession) -> List[BusinessNode]:
        """获取完整业务节点树（返回根节点，包含子节点）"""
        # 查询所有根节点
        query = select(BusinessNode).where(BusinessNode.parent_id.is_(None)).order_by(BusinessNode.sort_order, BusinessNode.id)
        result = await db.execute(query)
        root_nodes = list(result.scalars().all())

        # 递归加载所有子节点（使用eager loading提高性能）
        for node in root_nodes:
            await BusinessNodeService._load_children_recursive(db, node)

        return root_nodes

    @staticmethod
    async def _load_children_recursive(db: AsyncSession, node: BusinessNode):
        """递归加载子节点"""
        query = select(BusinessNode).where(BusinessNode.parent_id == node.id).order_by(BusinessNode.sort_order, BusinessNode.id)
        result = await db.execute(query)
        children = list(result.scalars().all())
        node.children = children
        for child in children:
            await BusinessNodeService._load_children_recursive(db, child)

    @staticmethod
    async def create(
        db: AsyncSession,
        node_in: BusinessNodeCreate,
        created_by: int,
    ) -> BusinessNode:
        """创建业务节点"""
        # 检查父节点是否存在
        if node_in.parent_id is not None:
            parent = await BusinessNodeService.get_by_id(db, node_in.parent_id)
            if not parent:
                raise ValueError(f"Parent node {node_in.parent_id} not found")

        node = BusinessNode(
            name=node_in.name,
            description=node_in.description,
            parent_id=node_in.parent_id,
            sort_order=node_in.sort_order,
            gateway_id=node_in.gateway_id,
            created_by=created_by,
        )
        db.add(node)
        await db.commit()
        await db.refresh(node)
        return node

    @staticmethod
    async def update(
        db: AsyncSession,
        node: BusinessNode,
        node_in: BusinessNodeUpdate,
    ) -> BusinessNode:
        """更新业务节点"""
        # 检查父节点是否存在
        if node_in.parent_id is not None and node_in.parent_id != node.parent_id:
            # 不能设置为自己
            if node_in.parent_id == node.id:
                raise ValueError("Cannot set parent to self")
            # 检查是否会导致循环引用
            if await BusinessNodeService._would_create_cycle(db, node.id, node_in.parent_id):
                raise ValueError("Cannot create circular reference in tree")
            # 检查父节点是否存在
            parent = await BusinessNodeService.get_by_id(db, node_in.parent_id)
            if not parent:
                raise ValueError(f"Parent node {node_in.parent_id} not found")

        # 更新字段
        update_data = node_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(node, field, value)

        await db.commit()
        await db.refresh(node)
        return node

    @staticmethod
    async def _would_create_cycle(db: AsyncSession, node_id: int, new_parent_id: int) -> bool:
        """检查是否会导致循环引用"""
        current_id = new_parent_id
        while current_id is not None:
            if current_id == node_id:
                return True
            current = await BusinessNodeService.get_by_id(db, current_id)
            if not current:
                break
            current_id = current.parent_id
        return False

    @staticmethod
    async def delete(db: AsyncSession, node: BusinessNode):
        """删除业务节点（级联删除子节点）"""
        await db.delete(node)
        await db.commit()
