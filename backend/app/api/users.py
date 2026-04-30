from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResetPassword,
    UserResponse,
    UserListResponse,
)
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["用户管理"])


def is_super_admin(user: User) -> bool:
    """检查用户是否是超级管理员"""
    return user.role in ("super_admin", "superadmin")


@router.get("", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=100, description="每页数量"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    role: Optional[str] = Query(None, description="用户角色"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取用户列表（仅超级管理员）"""
    if not is_super_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足",
        )
    total, users = await UserService.get_users(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active,
        role=role,
    )
    return UserListResponse(total=total, items=users)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建用户（仅超级管理员）"""
    if not is_super_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足",
        )
    # 检查用户名是否已存在
    existing_user = await UserService.get_user_by_username(db, user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )

    # 检查邮箱是否已存在
    existing_user = await UserService.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在",
        )

    # 创建用户
    user = await UserService.create_user(
        db=db,
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,
        is_active=user_in.is_active,
        role=user_in.role,
        real_name=user_in.real_name,
        created_by=current_user.id,
    )

    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取用户详情（仅超级管理员或用户自己）"""
    if not is_super_admin(current_user) and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足",
        )
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新用户信息（仅超级管理员）"""
    if not is_super_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足",
        )
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    # 检查用户名是否冲突
    if user_in.username and user_in.username != user.username:
        existing_user = await UserService.get_user_by_username(db, user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在",
            )

    # 检查邮箱是否冲突
    if user_in.email and user_in.email != user.email:
        existing_user = await UserService.get_user_by_email(db, user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在",
            )

    # 更新用户
    user = await UserService.update_user(
        db=db,
        user=user,
        username=user_in.username,
        email=user_in.email,
        real_name=user_in.real_name,
        role=user_in.role,
        is_active=user_in.is_active,
    )

    return user


@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    password_in: UserResetPassword,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """重置用户密码（仅超级管理员）"""
    if not is_super_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足",
        )
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    await UserService.reset_password(db, user, password_in.newPassword)

    return {"message": "密码重置成功"}


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除用户（仅超级管理员，不能删除自己）"""
    if not is_super_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足",
        )
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    # 不能删除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己",
        )

    await UserService.delete_user(db, user)

    return None
