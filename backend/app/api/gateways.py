from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_superuser
from app.models.user import User
from app.models.gateway import Gateway
from app.schemas.gateway import (
    GatewayCreate,
    GatewayUpdate,
    GatewayResponse,
    GatewayDetailResponse,
)
from app.services.gateway import GatewayService
from app.services.system_user import SystemUserService

router = APIRouter(prefix="/gateways", tags=["网关"])


@router.get("", response_model=List[GatewayResponse])
async def get_gateways(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取网关列表"""
    total, gateways = await GatewayService.get_list(
        db=db, skip=skip, limit=limit, search=search
    )
    return gateways


@router.post("", response_model=GatewayResponse, status_code=status.HTTP_201_CREATED)
async def create_gateway(
    gateway_in: GatewayCreate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """创建网关"""
    # Check if system_user exists
    system_user = await SystemUserService.get_by_id(db, gateway_in.system_user_id)
    if not system_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="系统用户不存在"
        )

    gateway = await GatewayService.create(
        db=db, gateway_in=gateway_in, created_by=current_user.id
    )
    return gateway


@router.get("/{gateway_id}", response_model=GatewayDetailResponse)
async def get_gateway(
    gateway_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取网关详情"""
    gateway = await GatewayService.get_by_id(db, gateway_id)
    if not gateway:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="网关不存在"
        )
    return gateway


@router.put("/{gateway_id}", response_model=GatewayResponse)
async def update_gateway(
    gateway_id: int,
    gateway_in: GatewayUpdate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """更新网关"""
    gateway = await GatewayService.get_by_id(db, gateway_id)
    if not gateway:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="网关不存在"
        )
    # Check if system_user exists if provided
    if gateway_in.system_user_id:
        system_user = await SystemUserService.get_by_id(db, gateway_in.system_user_id)
        if not system_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="系统用户不存在"
            )

    gateway = await GatewayService.update(db, gateway, gateway_in)
    return gateway


@router.delete("/{gateway_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gateway(
    gateway_id: int,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """删除网关"""
    gateway = await GatewayService.get_by_id(db, gateway_id)
    if not gateway:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="网关不存在"
        )
    await GatewayService.delete(db, gateway)
    return None
