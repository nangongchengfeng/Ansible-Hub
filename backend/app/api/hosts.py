from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_superuser
from app.models.user import User
from app.schemas.host import (
    HostCreate,
    HostUpdate,
    HostResponse,
    HostListResponse,
    HostDetailResponse,
    HostMoveRequest,
    ResolvedConnectionConfig,
)
from app.services.host import HostService

router = APIRouter(prefix="/hosts", tags=["主机管理"])


@router.get("", response_model=HostListResponse)
async def get_hosts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    business_node_id: Optional[int] = Query(None),
    is_enabled: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取主机列表"""
    total, hosts = await HostService.get_list(
        db=db,
        skip=skip,
        limit=limit,
        business_node_id=business_node_id,
        is_enabled=is_enabled,
        search=search,
    )
    return HostListResponse(total=total, items=hosts)


@router.post("", response_model=HostResponse, status_code=status.HTTP_201_CREATED)
async def create_host(
    host_in: HostCreate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """创建主机"""
    try:
        host = await HostService.create(
            db=db,
            host_in=host_in,
            created_by=current_user.id,
        )
        return host
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{host_id}", response_model=HostDetailResponse)
async def get_host(
    host_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取主机详情"""
    host = await HostService.get_by_id(db, host_id)
    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="主机不存在",
        )
    # Create response object with resolved connection
    response = HostDetailResponse.model_validate(host)
    response.resolved_connection = await HostService.resolve_connection_config(db, host)
    return response


@router.get("/{host_id}/connection-config", response_model=ResolvedConnectionConfig)
async def get_host_connection_config(
    host_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取主机的完整连接配置（含继承）"""
    host = await HostService.get_by_id(db, host_id)
    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="主机不存在",
        )
    connection_config = await HostService.resolve_connection_config(db, host)
    return connection_config


@router.put("/{host_id}", response_model=HostResponse)
async def update_host(
    host_id: int,
    host_in: HostUpdate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """更新主机信息"""
    host = await HostService.get_by_id(db, host_id)
    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="主机不存在",
        )
    host = await HostService.update(db, host, host_in)
    return host


@router.patch("/{host_id}/toggle")
async def toggle_host(
    host_id: int,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """启用/禁用主机"""
    host = await HostService.get_by_id(db, host_id)
    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="主机不存在",
        )
    host = await HostService.toggle(db, host)
    return {"id": host.id, "is_enabled": host.is_enabled}


@router.post("/{host_id}/move")
async def move_host(
    host_id: int,
    move_in: HostMoveRequest,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """移动主机到其他业务节点"""
    host = await HostService.get_by_id(db, host_id)
    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="主机不存在",
        )
    try:
        host = await HostService.move(db, host, move_in.target_business_node_id)
        return {"message": "主机移动成功"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{host_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_host(
    host_id: int,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """删除主机"""
    host = await HostService.get_by_id(db, host_id)
    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="主机不存在",
        )
    await HostService.delete(db, host)
    return None
