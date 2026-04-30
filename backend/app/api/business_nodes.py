from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_superuser
from app.models.user import User
from app.models.business_node import BusinessNode
from app.schemas.business_node import (
    BusinessNodeCreate,
    BusinessNodeUpdate,
    BusinessNodeResponse,
    BusinessNodeTreeItem,
    BusinessNodePermissionWithUser,
    BusinessNodePermissionsUpdate,
    BusinessNodeGatewayUpdate,
)
from app.services.business_node import BusinessNodeService

router = APIRouter(prefix="/business-nodes", tags=["业务节点"])


def _build_tree_item(node: BusinessNode) -> BusinessNodeTreeItem:
    """递归构建树状结构"""
    item = BusinessNodeTreeItem(
        id=node.id,
        name=node.name,
        description=node.description,
        parent_id=node.parent_id,
        sort_order=node.sort_order,
        gateway_id=node.gateway_id,
        created_by=node.created_by,
        created_at=node.created_at,
        updated_at=node.updated_at,
        children=[],
    )
    for child in node.children:
        item.children.append(_build_tree_item(child))
    return item


@router.get("/tree", response_model=List[BusinessNodeTreeItem])
async def get_business_nodes_tree(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取业务节点树状结构（含权限过滤）"""
    accessible_ids = await BusinessNodeService.get_accessible_node_ids(db, current_user, "view")
    nodes = await BusinessNodeService.get_filtered_tree(db, accessible_ids)
    return [_build_tree_item(node) for node in nodes]


@router.get("", response_model=List[BusinessNodeResponse])
async def get_business_nodes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    parent_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取业务节点列表（平铺）"""
    # TODO: 添加权限过滤
    total, nodes = await BusinessNodeService.get_list(
        db=db,
        skip=skip,
        limit=limit,
        parent_id=parent_id,
    )
    return nodes


@router.post("", response_model=BusinessNodeResponse, status_code=status.HTTP_201_CREATED)
async def create_business_node(
    node_in: BusinessNodeCreate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """创建业务节点"""
    try:
        node = await BusinessNodeService.create(
            db=db,
            node_in=node_in,
            created_by=current_user.id,
        )
        return node
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{node_id}", response_model=BusinessNodeResponse)
async def get_business_node(
    node_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取业务节点详情"""
    node = await BusinessNodeService.get_by_id(db, node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business node not found",
        )
    # TODO: 添加权限检查
    return node


@router.put("/{node_id}", response_model=BusinessNodeResponse)
async def update_business_node(
    node_id: int,
    node_in: BusinessNodeUpdate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """更新业务节点"""
    node = await BusinessNodeService.get_by_id(db, node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business node not found",
        )
    try:
        node = await BusinessNodeService.update(db, node, node_in)
        return node
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business_node(
    node_id: int,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """删除业务节点（级联删除子节点）"""
    node = await BusinessNodeService.get_by_id(db, node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business node not found",
        )
    await BusinessNodeService.delete(db, node)
    return None


# Permission endpoints

@router.get("/{node_id}/permissions", response_model=List[BusinessNodePermissionWithUser])
async def get_business_node_permissions(
    node_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取业务节点权限列表"""
    # Check if node exists
    node = await BusinessNodeService.get_by_id(db, node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business node not found",
        )
    # TODO: Add permission check
    permissions = await BusinessNodeService.get_permissions(db, node_id)
    return permissions


@router.put("/{node_id}/permissions", response_model=List[BusinessNodePermissionWithUser])
async def set_business_node_permissions(
    node_id: int,
    permissions_in: BusinessNodePermissionsUpdate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """设置业务节点权限（覆盖）"""
    # Check if node exists
    node = await BusinessNodeService.get_by_id(db, node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business node not found",
        )
    permissions = await BusinessNodeService.set_permissions(
        db, node_id, permissions_in.permissions, current_user.id
    )
    return permissions


@router.put("/{node_id}/gateway", response_model=BusinessNodeResponse)
async def update_business_node_gateway(
    node_id: int,
    gateway_in: BusinessNodeGatewayUpdate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """绑定网关到业务节点"""
    node = await BusinessNodeService.get_by_id(db, node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business node not found",
        )
    node = await BusinessNodeService.update_gateway(db, node, gateway_in.gateway_id)
    return node


@router.get("/{node_id}/hosts")
async def get_business_node_hosts(
    node_id: int,
    include_children: bool = Query(True, description="Include hosts from child nodes"),
    only_enabled: bool = Query(True, description="Only show enabled hosts"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取业务节点及其子节点的所有主机"""
    # Check if node exists and user has permission
    node = await BusinessNodeService.get_by_id(db, node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business node not found",
        )
    # TODO: Add permission check, Host model, and actual implementation
    return {"items": [], "total": 0}

