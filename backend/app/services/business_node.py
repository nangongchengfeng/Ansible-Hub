from typing import Optional, List, Tuple, Set
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.business_node import BusinessNode
from app.models.business_node_permission import BusinessNodePermission
from app.models.user import User
from app.schemas.business_node import BusinessNodeCreate, BusinessNodeUpdate, BusinessNodePermissionCreate


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
    async def get_all_nodes(db: AsyncSession) -> List[BusinessNode]:
        """获取所有业务节点"""
        query = select(BusinessNode).order_by(BusinessNode.sort_order, BusinessNode.id)
        result = await db.execute(query)
        return list(result.scalars().all())

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

    # Permission-related methods

    @staticmethod
    async def get_permissions(db: AsyncSession, node_id: int) -> List[BusinessNodePermission]:
        """Get all permissions for a business node"""
        query = select(BusinessNodePermission).where(
            BusinessNodePermission.business_node_id == node_id
        ).options(selectinload(BusinessNodePermission.user))
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def set_permissions(
        db: AsyncSession,
        node_id: int,
        permissions_in: List[BusinessNodePermissionCreate],
        created_by: int,
    ) -> List[BusinessNodePermission]:
        """Set permissions for a business node (overwrites existing)"""
        # First delete all existing permissions
        delete_query = select(BusinessNodePermission).where(
            BusinessNodePermission.business_node_id == node_id
        )
        delete_result = await db.execute(delete_query)
        for perm in delete_result.scalars().all():
            await db.delete(perm)

        # Then add new permissions
        new_permissions = []
        for perm_in in permissions_in:
            perm = BusinessNodePermission(
                business_node_id=node_id,
                user_id=perm_in.user_id,
                permission_type=perm_in.permission_type,
                created_by=created_by,
            )
            db.add(perm)
            new_permissions.append(perm)

        await db.commit()

        # Refresh to get user data
        for perm in new_permissions:
            await db.refresh(perm, attribute_names=["user"])

        return new_permissions

    @staticmethod
    async def update_gateway(
        db: AsyncSession,
        node: BusinessNode,
        gateway_id: Optional[int],
    ) -> BusinessNode:
        """Update gateway for a business node"""
        node.gateway_id = gateway_id
        await db.commit()
        await db.refresh(node)
        return node

    @staticmethod
    async def get_accessible_node_ids(
        db: AsyncSession,
        user: User,
        required_permission: str = "view",
    ) -> Set[int]:
        """Get all node IDs that a user has access to (including inherited permissions)"""
        # Super admin has access to everything
        if hasattr(user, 'is_superuser') and user.is_superuser:
            query = select(BusinessNode.id)
            result = await db.execute(query)
            return set(result.scalars().all())

        # Get all permissions for this user
        query = select(BusinessNodePermission).where(
            BusinessNodePermission.user_id == user.id
        )
        result = await db.execute(query)
        user_permissions = list(result.scalars().all())

        # Check if user has the required permission (or higher)
        accessible_node_ids = set()
        permission_hierarchy = {"view": 1, "execute": 2, "manage": 3}
        required_level = permission_hierarchy.get(required_permission, 1)

        for perm in user_permissions:
            perm_level = permission_hierarchy.get(perm.permission_type, 1)
            if perm_level >= required_level:
                accessible_node_ids.add(perm.business_node_id)

        # Get all descendants of accessible nodes (they inherit permissions)
        all_nodes = await BusinessNodeService.get_all_nodes(db)
        node_children_map = {}
        for node in all_nodes:
            if node.parent_id not in node_children_map:
                node_children_map[node.parent_id] = []
            node_children_map[node.parent_id].append(node.id)

        # Add all descendants
        nodes_to_process = list(accessible_node_ids)
        while nodes_to_process:
            current_id = nodes_to_process.pop()
            if current_id in node_children_map:
                for child_id in node_children_map[current_id]:
                    if child_id not in accessible_node_ids:
                        accessible_node_ids.add(child_id)
                        nodes_to_process.append(child_id)

        return accessible_node_ids

    @staticmethod
    async def get_all_nodes(db: AsyncSession) -> List[BusinessNode]:
        """Get all business nodes"""
        query = select(BusinessNode)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_filtered_tree(
        db: AsyncSession,
        accessible_node_ids: Set[int],
    ) -> List[BusinessNode]:
        """Get business node tree filtered by accessible nodes"""
        # Get all accessible nodes
        query = select(BusinessNode).where(BusinessNode.id.in_(accessible_node_ids))
        result = await db.execute(query)
        accessible_nodes = list(result.scalars().all())
        node_map = {node.id: node for node in accessible_nodes}

        # Find root nodes (either parent is None or parent not accessible)
        root_nodes = []
        for node in accessible_nodes:
            if node.parent_id is None or node.parent_id not in node_map:
                root_nodes.append(node)

        # Build tree structure for accessible nodes only
        for node in accessible_nodes:
            node.children = []

        for node in accessible_nodes:
            if node.parent_id is not None and node.parent_id in node_map:
                node_map[node.parent_id].children.append(node)

        # Sort
        root_nodes.sort(key=lambda x: (x.sort_order, x.id))
        for node in accessible_nodes:
            node.children.sort(key=lambda x: (x.sort_order, x.id))

        return root_nodes

    @staticmethod
    async def check_permission(
        db: AsyncSession,
        node_id: int,
        user: User,
        required_permission: str = "view",
    ) -> bool:
        """Check if a user has permission for a node (including inherited permissions)"""
        accessible_ids = await BusinessNodeService.get_accessible_node_ids(
            db, user, required_permission
        )
        return node_id in accessible_ids
