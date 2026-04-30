from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_auditor_or_superuser
from app.models.user import User
from app.schemas.audit_log import (
    AuditLogResponse,
    AuditLogDetailResponse,
    AuditLogListResponse,
)
from app.services.audit_log import AuditLogService

router = APIRouter(prefix="/audit-logs", tags=["审计日志"])


@router.get("", response_model=AuditLogListResponse)
async def get_audit_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: Optional[int] = Query(None, description="按用户筛选"),
    action: Optional[str] = Query(None, description="按操作类型筛选"),
    resource_type: Optional[str] = Query(None, description="按资源类型筛选"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    search: Optional[str] = Query(None, description="搜索资源名称或用户名"),
    current_user: User = Depends(get_current_auditor_or_superuser),
    db: AsyncSession = Depends(get_db),
):
    """获取审计日志列表"""
    skip = (page - 1) * page_size
    total, logs = await AuditLogService.get_list(
        db=db,
        skip=skip,
        limit=page_size,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        start_time=start_time,
        end_time=end_time,
        search=search,
    )
    total_pages = (total + page_size - 1) // page_size

    return AuditLogListResponse(
        items=logs,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{audit_log_id}", response_model=AuditLogDetailResponse)
async def get_audit_log(
    audit_log_id: int,
    current_user: User = Depends(get_current_auditor_or_superuser),
    db: AsyncSession = Depends(get_db),
):
    """获取审计日志详情"""
    log = await AuditLogService.get_by_id(db, audit_log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="审计日志不存在",
        )

    # 添加变更对比
    response = AuditLogDetailResponse.model_validate(log)
    response.changes = log.changes

    return response
