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
)
from app.services.business_node import BusinessNodeService

router = APIRouter(prefix="/business-nodes", tags=["业务节点"])


def _build_tree_item(node: BusinessNode, node_map: dict, current_user: User) -> BusinessNodeTreeItem:
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
    # 从node_map中查找子节点
    for child_id, child_node in node_map.items():
        if child_node.parent_id == node.id:
            item.children.append(_build_tree_item(child_node, node_map, current_user))
    # 排序子节点
    item.children.sort(key=lambda x: (x.sort_order, x.id))
    return item


@router.get("/tree", response_model=List[BusinessNodeTreeItem])
async def get_business_nodes_tree(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取业务节点树状结构"""
    all_nodes = await BusinessNodeService.get_tree(db)

    # 构建节点映射
    node_map = {node.id: node for node in all_nodes}

    # 找出根节点
    root_nodes = [node for node in all_nodes if node.parent_id is None]
    root_nodes.sort(key=lambda x: (x.sort_order, x.id))

    # 构建树结构
    return [_build_tree_item(node, node_map, current_user) for node in root_nodes]


@router.get("", response_model=List[BusinessNodeResponse])
async def get_business_nodes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    parent_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取业务节点列表（平铺）"""
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
