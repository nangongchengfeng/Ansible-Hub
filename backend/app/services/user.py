from typing import Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.core.security import get_password_hash


class UserService:
    """用户服务"""

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """通过ID获取用户"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """通过用户名获取用户"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        role: Optional[UserRole] = None,
    ) -> tuple[int, list[User]]:
        """获取用户列表"""
        # 构建查询条件
        conditions = []
        if is_active is not None:
            conditions.append(User.is_active == is_active)
        if role is not None:
            conditions.append(User.role == role)

        # 总数查询
        count_query = select(func.count(User.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # 数据查询
        data_query = select(User).offset(skip).limit(limit)
        if conditions:
            data_query = data_query.where(and_(*conditions))
        data_query = data_query.order_by(User.id.desc())
        data_result = await db.execute(data_query)
        users = list(data_result.scalars().all())

        return total, users

    @staticmethod
    async def create_user(
        db: AsyncSession,
        username: str,
        email: str,
        password: str,
        is_active: bool = True,
        role: UserRole = UserRole.OPERATOR,
        real_name: Optional[str] = None,
        created_by: Optional[int] = None,
    ) -> User:
        """创建用户"""
        hashed_password = get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=is_active,
            role=role,
            real_name=real_name,
            created_by=created_by,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user: User,
        username: Optional[str] = None,
        email: Optional[str] = None,
        real_name: Optional[str] = None,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
    ) -> User:
        """更新用户"""
        if username is not None:
            user.username = username
        if email is not None:
            user.email = email
        if real_name is not None:
            user.real_name = real_name
        if role is not None:
            user.role = role
        if is_active is not None:
            user.is_active = is_active

        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def reset_password(
        db: AsyncSession,
        user: User,
        new_password: str,
    ) -> User:
        """重置密码"""
        user.hashed_password = get_password_hash(new_password)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user: User) -> None:
        """删除用户"""
        await db.delete(user)
        await db.commit()
