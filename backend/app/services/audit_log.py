from typing import Optional, List, Tuple, Dict, Any, Callable
from functools import wraps
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogCreate


class AuditLogService:
    """审计日志服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, audit_log_id: int) -> Optional[AuditLog]:
        """通过ID获取审计日志"""
        result = await db.execute(
            select(AuditLog)
            .where(AuditLog.id == audit_log_id)
            .options(selectinload(AuditLog.user))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        search: Optional[str] = None,
    ) -> Tuple[int, List[AuditLog]]:
        """获取审计日志列表"""
        # Build conditions
        conditions = []
        if user_id is not None:
            conditions.append(AuditLog.user_id == user_id)
        if action:
            conditions.append(AuditLog.action == action)
        if resource_type:
            conditions.append(AuditLog.resource_type == resource_type)
        if start_time:
            conditions.append(AuditLog.created_at >= start_time)
        if end_time:
            conditions.append(AuditLog.created_at <= end_time)
        if search:
            conditions.append(
                or_(
                    AuditLog.username.contains(search),
                    AuditLog.resource_name.contains(search),
                )
            )

        # Count
        count_query = select(AuditLog.id)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # Query data
        data_query = select(AuditLog).options(
            selectinload(AuditLog.user)
        )
        if conditions:
            data_query = data_query.where(and_(*conditions))
        data_query = data_query.order_by(desc(AuditLog.created_at)).offset(skip).limit(limit)
        data_result = await db.execute(data_query)
        logs = list(data_result.scalars().all())

        return total, logs

    @staticmethod
    async def create(
        db: AsyncSession,
        log_in: AuditLogCreate,
    ) -> AuditLog:
        """创建审计日志"""
        log = AuditLog(
            user_id=log_in.user_id,
            username=log_in.username,
            action=log_in.action,
            resource_type=log_in.resource_type,
            resource_id=log_in.resource_id,
            resource_name=log_in.resource_name,
            old_values=log_in.old_values,
            new_values=log_in.new_values,
            ip_address=log_in.ip_address,
            user_agent=log_in.user_agent,
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log

    @staticmethod
    async def log_action(
        db: AsyncSession,
        user: Optional[User],
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        resource_name: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        """记录审计日志（便捷方法）"""
        log_in = AuditLogCreate(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            old_values=old_values,
            new_values=new_values,
            user_id=user.id if user else None,
            username=user.username if user else None,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await AuditLogService.create(db, log_in)


def audit_log(
    action: str,
    resource_type: str,
    get_resource_id: Optional[Callable] = None,
    get_resource_name: Optional[Callable] = None,
    get_old_values: Optional[Callable] = None,
    get_new_values: Optional[Callable] = None,
):
    """
    审计日志装饰器

    :param action: 操作类型 (create/update/delete)
    :param resource_type: 资源类型
    :param get_resource_id: 从函数返回值获取资源ID的回调
    :param get_resource_name: 从函数返回值获取资源名称的回调
    :param get_old_values: 获取旧值的回调（通常在更新前调用）
    :param get_new_values: 获取新值的回调
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 尝试从kwargs获取request和db
            request = kwargs.get('request')
            db = kwargs.get('db')

            # 尝试获取当前用户
            current_user: Optional[User] = kwargs.get('current_user')
            if not current_user and hasattr(request, 'state') and hasattr(request.state, 'user'):
                current_user = request.state.user

            # 尝试获取IP地址和User Agent
            ip_address = None
            user_agent = None
            if request:
                if hasattr(request, 'client') and request.client:
                    ip_address = request.client.host
                if hasattr(request, 'headers'):
                    user_agent = request.headers.get('user-agent')

            # 获取旧值（在执行前）
            old_values = None
            if get_old_values:
                try:
                    old_values = await get_old_values(*args, **kwargs)
                except Exception:
                    pass

            # 执行原始函数
            result = await func(*args, **kwargs)

            # 获取新值
            new_values = None
            if get_new_values:
                try:
                    new_values = get_new_values(result)
                except Exception:
                    pass

            # 获取资源ID
            resource_id = None
            if get_resource_id:
                try:
                    resource_id = get_resource_id(result)
                except Exception:
                    pass

            # 获取资源名称
            resource_name = None
            if get_resource_name:
                try:
                    resource_name = get_resource_name(result)
                except Exception:
                    pass

            # 创建审计日志
            if db:
                log_data = AuditLogCreate(
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    resource_name=resource_name,
                    old_values=old_values,
                    new_values=new_values,
                    user_id=current_user.id if current_user else None,
                    username=current_user.username if current_user else None,
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
                await AuditLogService.create(db, log_data)

            return result
        return wrapper
    return decorator
