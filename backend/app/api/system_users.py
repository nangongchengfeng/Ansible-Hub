from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_superuser
from app.models.user import User
from app.models.system_user import SystemUser
from app.schemas.system_user import (
    SystemUserCreate,
    SystemUserUpdate,
    SystemUserResponse,
    SystemUserListResponse,
    SystemUserDetailResponse,
)
from app.services.system_user import SystemUserService

router = APIRouter(prefix="/system-users", tags=["系统用户"])


@router.get("", response_model=SystemUserListResponse)
async def get_system_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    auth_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取系统用户列表"""
    total, system_users = await SystemUserService.get_list(
        db=db, skip=skip, limit=limit, auth_type=auth_type, search=search
    )
    # Set can_view_secret for each user
    for su in system_users:
        is_owner = su.created_by == current_user.id
        is_super_admin = getattr(current_user, "role", None) in ["super_admin", "superadmin"]
        su.can_view_secret = is_owner or is_super_admin
    return SystemUserListResponse(total=total, items=system_users)


@router.post("", response_model=SystemUserResponse, status_code=status.HTTP_201_CREATED)
async def create_system_user(
    system_user_in: SystemUserCreate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """创建系统用户"""
    # Validate auth_type has required fields
    if system_user_in.auth_type == "private_key" and not system_user_in.private_key:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="私钥认证必须提供private_key"
        )
    if system_user_in.auth_type == "password" and not system_user_in.password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="密码认证必须提供password"
        )

    system_user = await SystemUserService.create(
        db=db, system_user_in=system_user_in, created_by=current_user.id
    )
    system_user.can_view_secret = True
    return system_user


@router.get("/{system_user_id}", response_model=SystemUserDetailResponse)
async def get_system_user(
    system_user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取系统用户详情"""
    system_user = await SystemUserService.get_by_id(db, system_user_id)
    if not system_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="系统用户不存在"
        )
    # Fill sensitive fields if authorized
    system_user = SystemUserService.fill_sensitive_fields(system_user, current_user)
    return system_user


@router.put("/{system_user_id}", response_model=SystemUserResponse)
async def update_system_user(
    system_user_id: int,
    system_user_in: SystemUserUpdate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """更新系统用户"""
    system_user = await SystemUserService.get_by_id(db, system_user_id)
    if not system_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="系统用户不存在"
        )
    system_user = await SystemUserService.update(db, system_user, system_user_in)
    # Set can_view_secret
    is_owner = system_user.created_by == current_user.id
    is_super_admin = getattr(current_user, "role", None) in ["super_admin", "superadmin"]
    system_user.can_view_secret = is_owner or is_super_admin
    return system_user


@router.delete("/{system_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_system_user(
    system_user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """删除系统用户"""
    system_user = await SystemUserService.get_by_id(db, system_user_id)
    if not system_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="系统用户不存在"
        )
    await SystemUserService.delete(db, system_user)
    return None
