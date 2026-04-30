from typing import Optional, List, Tuple
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.system_user import SystemUser
from app.models.user import User
from app.schemas.system_user import SystemUserCreate, SystemUserUpdate
from app.core.security import encrypt_data, decrypt_data


class SystemUserService:
    """系统用户服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, system_user_id: int) -> Optional[SystemUser]:
        """通过ID获取系统用户"""
        result = await db.execute(select(SystemUser).where(SystemUser.id == system_user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        auth_type: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[int, List[SystemUser]]:
        """获取系统用户列表"""
        # Build conditions
        conditions = []
        if auth_type:
            conditions.append(SystemUser.auth_type == auth_type)
        if search:
            conditions.append(SystemUser.name.contains(search))

        # Count
        count_query = select(SystemUser.id)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # Query data
        data_query = select(SystemUser)
        if conditions:
            data_query = data_query.where(and_(*conditions))
        data_query = data_query.order_by(SystemUser.created_at.desc()).offset(skip).limit(limit)
        data_result = await db.execute(data_query)
        system_users = list(data_result.scalars().all())

        return total, system_users

    @staticmethod
    async def create(
        db: AsyncSession,
        system_user_in: SystemUserCreate,
        created_by: int,
    ) -> SystemUser:
        """创建系统用户"""
        # Encrypt sensitive data
        private_key_cipher = encrypt_data(system_user_in.private_key) if system_user_in.private_key else None
        password_cipher = encrypt_data(system_user_in.password) if system_user_in.password else None
        become_password_cipher = encrypt_data(system_user_in.become_password) if system_user_in.become_password else None

        system_user = SystemUser(
            name=system_user_in.name,
            username=system_user_in.username,
            auth_type=system_user_in.auth_type,
            private_key_cipher=private_key_cipher,
            password_cipher=password_cipher,
            become_method=system_user_in.become_method,
            become_username=system_user_in.become_username,
            become_password_cipher=become_password_cipher,
            created_by=created_by,
        )
        db.add(system_user)
        await db.commit()
        await db.refresh(system_user)
        return system_user

    @staticmethod
    async def update(
        db: AsyncSession,
        system_user: SystemUser,
        system_user_in: SystemUserUpdate,
    ) -> SystemUser:
        """更新系统用户"""
        update_data = system_user_in.model_dump(exclude_unset=True)

        # Handle sensitive fields with encryption
        if "private_key" in update_data:
            system_user.private_key_cipher = encrypt_data(update_data["private_key"]) if update_data["private_key"] else None
            del update_data["private_key"]
        if "password" in update_data:
            system_user.password_cipher = encrypt_data(update_data["password"]) if update_data["password"] else None
            del update_data["password"]
        if "become_password" in update_data:
            system_user.become_password_cipher = encrypt_data(update_data["become_password"]) if update_data["become_password"] else None
            del update_data["become_password"]

        # Update other fields
        for field, value in update_data.items():
            setattr(system_user, field, value)

        await db.commit()
        await db.refresh(system_user)
        return system_user

    @staticmethod
    async def delete(db: AsyncSession, system_user: SystemUser):
        """删除系统用户"""
        # TODO: Check if system_user is used by any gateway or host before deleting
        await db.delete(system_user)
        await db.commit()

    @staticmethod
    def fill_sensitive_fields(
        system_user: SystemUser,
        current_user: User,
    ) -> SystemUser:
        """填充敏感字段（仅创建者和super_admin可见）"""
        # Check if current user can view secrets
        is_owner = system_user.created_by == current_user.id
        is_super_admin = getattr(current_user, "role", None) in ["super_admin", "superadmin"]

        if is_owner or is_super_admin:
            # Decrypt sensitive fields
            if system_user.private_key_cipher:
                system_user.private_key = decrypt_data(system_user.private_key_cipher)
            else:
                system_user.private_key = None
            if system_user.password_cipher:
                system_user.password = decrypt_data(system_user.password_cipher)
            else:
                system_user.password = None
            if system_user.become_password_cipher:
                system_user.become_password = decrypt_data(system_user.become_password_cipher)
            else:
                system_user.become_password = None
            system_user.can_view_secret = True
        else:
            system_user.private_key = None
            system_user.password = None
            system_user.become_password = None
            system_user.can_view_secret = False

        return system_user
