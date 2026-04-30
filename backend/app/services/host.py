from typing import Optional, List, Tuple, Set, Dict
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.host import Host
from app.models.business_node import BusinessNode
from app.schemas.host import HostCreate, HostUpdate, ResolutionPathItem, ResolvedConnectionConfig
from app.services.business_node import BusinessNodeService
from app.services.gateway import GatewayService


class HostService:
    """主机服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, host_id: int) -> Optional[Host]:
        """通过ID获取主机"""
        result = await db.execute(
            select(Host).where(Host.id == host_id).options(
                selectinload(Host.business_node),
                selectinload(Host.system_user),
                selectinload(Host.gateway),
                selectinload(Host.creator),
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        business_node_id: Optional[int] = None,
        is_enabled: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[int, List[Host]]:
        """获取主机列表"""
        # Build conditions
        conditions = []
        if business_node_id is not None:
            conditions.append(Host.business_node_id == business_node_id)
        if is_enabled is not None:
            conditions.append(Host.is_enabled == is_enabled)
        if search:
            conditions.append(
                or_(
                    Host.name.contains(search),
                    Host.ip_internal.contains(search),
                    Host.ip_external.contains(search),
                )
            )

        # Count
        count_query = select(Host.id)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # Query data
        data_query = select(Host).options(
            selectinload(Host.business_node),
            selectinload(Host.system_user),
            selectinload(Host.gateway),
        )
        if conditions:
            data_query = data_query.where(and_(*conditions))
        data_query = data_query.order_by(Host.created_at.desc()).offset(skip).limit(limit)
        data_result = await db.execute(data_query)
        hosts = list(data_result.scalars().all())

        return total, hosts

    @staticmethod
    async def get_by_business_node(
        db: AsyncSession,
        business_node_id: int,
        include_children: bool = True,
        only_enabled: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[int, List[Host]]:
        """获取业务节点及其子节点的主机"""
        # Get all relevant business node IDs
        business_node_ids: Set[int] = {business_node_id}
        if include_children:
            # Get all descendant business nodes
            all_nodes = await BusinessNodeService.get_all_nodes(db)
            # Build a map from parent_id to children
            children_map: dict[int, List[int]] = {}
            for node in all_nodes:
                if node.parent_id not in children_map:
                    children_map[node.parent_id] = []
                children_map[node.parent_id].append(node.id)
            # BFS to collect all children
            queue = [business_node_id]
            while queue:
                current_id = queue.pop(0)
                if current_id in children_map:
                    for child_id in children_map[current_id]:
                        if child_id not in business_node_ids:
                            business_node_ids.add(child_id)
                            queue.append(child_id)

        # Build conditions
        conditions = [Host.business_node_id.in_(business_node_ids)]
        if only_enabled:
            conditions.append(Host.is_enabled == True)

        # Count
        count_query = select(Host.id).where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # Query data
        data_query = select(Host).where(and_(*conditions)).options(
            selectinload(Host.business_node),
            selectinload(Host.system_user),
            selectinload(Host.gateway),
        ).order_by(Host.created_at.desc()).offset(skip).limit(limit)
        data_result = await db.execute(data_query)
        hosts = list(data_result.scalars().all())

        return total, hosts

    @staticmethod
    async def create(
        db: AsyncSession,
        host_in: HostCreate,
        created_by: int,
    ) -> Host:
        """创建主机"""
        # Check if business node exists
        business_node = await BusinessNodeService.get_by_id(db, host_in.business_node_id)
        if not business_node:
            raise ValueError(f"Business node {host_in.business_node_id} not found")

        host = Host(
            name=host_in.name,
            business_node_id=host_in.business_node_id,
            ip_internal=host_in.ip_internal,
            ip_external=host_in.ip_external,
            ip_preference=host_in.ip_preference,
            ssh_port=host_in.ssh_port,
            cloud_provider=host_in.cloud_provider,
            system_user_id=host_in.system_user_id,
            gateway_id=host_in.gateway_id,
            created_by=created_by,
        )
        db.add(host)
        await db.commit()
        await db.refresh(host)
        # Load relationships
        await db.execute(select(Host).where(Host.id == host.id).options(
            selectinload(Host.business_node),
            selectinload(Host.system_user),
            selectinload(Host.gateway),
        ))
        return host

    @staticmethod
    async def update(
        db: AsyncSession,
        host: Host,
        host_in: HostUpdate,
    ) -> Host:
        """更新主机"""
        update_data = host_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(host, field, value)

        await db.commit()
        await db.refresh(host)
        # Load relationships
        await db.execute(select(Host).where(Host.id == host.id).options(
            selectinload(Host.business_node),
            selectinload(Host.system_user),
            selectinload(Host.gateway),
        ))
        return host

    @staticmethod
    async def toggle(
        db: AsyncSession,
        host: Host,
    ) -> Host:
        """切换主机启用状态"""
        host.is_enabled = not host.is_enabled
        await db.commit()
        await db.refresh(host)
        return host

    @staticmethod
    async def move(
        db: AsyncSession,
        host: Host,
        target_business_node_id: int,
    ) -> Host:
        """移动主机到其他业务节点"""
        # Check if target business node exists
        target_node = await BusinessNodeService.get_by_id(db, target_business_node_id)
        if not target_node:
            raise ValueError(f"Business node {target_business_node_id} not found")
        # Update
        host.business_node_id = target_business_node_id
        await db.commit()
        await db.refresh(host)
        return host

    @staticmethod
    async def delete(db: AsyncSession, host: Host) -> None:
        """删除主机"""
        await db.delete(host)
        await db.commit()

    @staticmethod
    async def resolve_connection_config(db: AsyncSession, host: Host) -> ResolvedConnectionConfig:
        """解析主机连接配置（含完整继承逻辑）"""
        resolution_path: List[ResolutionPathItem] = []
        resolved_values: Dict[str, object] = {}

        # First, collect the hierarchy: host -> business node -> ... -> root
        hierarchy = [host]
        if host.business_node:
            current_node = host.business_node
            while current_node:
                hierarchy.append(current_node)
                if current_node.parent_id:
                    # Need to load parent
                    parent_node = await BusinessNodeService.get_by_id(db, current_node.parent_id)
                    if parent_node:
                        current_node = parent_node
                    else:
                        break
                else:
                    break

        # Resolve IP
        ip = None
        # First try host's preferred IP
        if host.ip_preference == "internal" and host.ip_internal:
            ip = host.ip_internal
            resolution_path.append(ResolutionPathItem(
                level="host", field="ip_internal", value=ip, status="explicit"
            ))
        elif host.ip_preference == "external" and host.ip_external:
            ip = host.ip_external
            resolution_path.append(ResolutionPathItem(
                level="host", field="ip_external", value=ip, status="explicit"
            ))
        # Fallback to whichever is available on host
        if not ip and host.ip_internal:
            ip = host.ip_internal
            resolution_path.append(ResolutionPathItem(
                level="host", field="ip_internal", value=ip, status="explicit"
            ))
        elif not ip and host.ip_external:
            ip = host.ip_external
            resolution_path.append(ResolutionPathItem(
                level="host", field="ip_external", value=ip, status="explicit"
            ))
        resolved_values["ip"] = ip

        # Resolve SSH port
        ssh_port = host.ssh_port if host.ssh_port else 22
        if host.ssh_port:
            resolution_path.append(ResolutionPathItem(
                level="host", field="ssh_port", value=ssh_port, status="explicit"
            ))
        else:
            resolution_path.append(ResolutionPathItem(
                level="default", field="ssh_port", value=22, status="inherited"
            ))
        resolved_values["ssh_port"] = ssh_port

        # Resolve system user
        system_user = host.system_user
        system_user_id = host.system_user_id
        if system_user_id:
            resolution_path.append(ResolutionPathItem(
                level="host", field="system_user_id", value=system_user_id, status="explicit"
            ))
        else:
            # Try to inherit from business nodes
            for node in hierarchy[1:]:  # Skip host, start from business nodes
                if hasattr(node, 'system_user_id') and node.system_user_id:
                    system_user_id = node.system_user_id
                    resolution_path.append(ResolutionPathItem(
                        level=f"business_node_{node.id}", field="system_user_id",
                        value=system_user_id, status="inherited"
                    ))
                    break
        resolved_values["system_user_id"] = system_user_id

        # Resolve gateway
        gateway = host.gateway
        gateway_id = host.gateway_id
        gateway_source = None
        if gateway_id:
            gateway_source = "host"
            resolution_path.append(ResolutionPathItem(
                level="host", field="gateway_id", value=gateway_id, status="explicit"
            ))
        else:
            # Try to inherit from business nodes
            for node in hierarchy[1:]:  # Skip host, start from business nodes
                if node.gateway_id:
                    gateway_id = node.gateway_id
                    gateway_source = f"business_node_{node.id}"
                    # Load the gateway if needed
                    if not gateway:
                        gateway = await GatewayService.get_by_id(db, gateway_id)
                    resolution_path.append(ResolutionPathItem(
                        level=f"business_node_{node.id}", field="gateway_id",
                        value=gateway_id, status="inherited"
                    ))
                    break
        resolved_values["gateway_id"] = gateway_id

        # Build resolved config for Ansible/Paramiko
        resolved_config = None
        if ip:
            resolved_config = {
                "ansible_host": ip,
                "ansible_port": ssh_port,
            }
            if system_user:
                resolved_config["ansible_user"] = system_user.username
                if system_user.auth_type == "private_key" and system_user.private_key:
                    resolved_config["ansible_ssh_private_key"] = system_user.private_key
                elif system_user.auth_type == "password" and system_user.password_cipher:
                    resolved_config["ansible_ssh_pass"] = system_user.password_cipher
                if system_user.become_method:
                    resolved_config["ansible_become"] = True
                    resolved_config["ansible_become_method"] = system_user.become_method
                    if system_user.become_username:
                        resolved_config["ansible_become_user"] = system_user.become_username
                    if system_user.become_password_cipher:
                        resolved_config["ansible_become_pass"] = system_user.become_password_cipher
            if gateway and gateway.system_user:
                gateway_config = {
                    "host": gateway.ip,
                    "port": gateway.port,
                    "user": gateway.system_user.username,
                }
                if gateway.system_user.auth_type == "private_key" and gateway.system_user.private_key:
                    gateway_config["private_key"] = gateway.system_user.private_key
                elif gateway.system_user.auth_type == "password" and gateway.system_user.password_cipher:
                    gateway_config["password"] = gateway.system_user.password_cipher
                resolved_config["ansible_ssh_common_args"] = (
                    f"-o ProxyJump={gateway.system_user.username}@{gateway.ip}:{gateway.port}"
                )
                resolved_config["gateway"] = gateway_config

        return ResolvedConnectionConfig(
            host_id=host.id,
            host_name=host.name,
            ip=ip,
            ssh_port=ssh_port,
            system_user_id=system_user_id,
            system_user=system_user,
            gateway_id=gateway_id,
            gateway=gateway,
            gateway_source=gateway_source,
            resolution_path=resolution_path,
            resolved_config=resolved_config,
        )
