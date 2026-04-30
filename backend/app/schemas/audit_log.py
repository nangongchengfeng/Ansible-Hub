from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AuditLogBase(BaseModel):
    """审计日志基础信息"""
    action: str = Field(..., min_length=1, max_length=50)
    resource_type: Optional[str] = Field(None, max_length=50)
    resource_id: Optional[int] = Field(None)
    resource_name: Optional[str] = Field(None, max_length=255)
    old_values: Optional[Dict[str, Any]] = Field(None)
    new_values: Optional[Dict[str, Any]] = Field(None)


class AuditLogCreate(AuditLogBase):
    """创建审计日志（内部使用）"""
    user_id: Optional[int] = Field(None)
    username: Optional[str] = Field(None, max_length=50)
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None)


class AuditLogSimple(BaseModel):
    """审计日志简单信息"""
    id: int
    user_id: Optional[int]
    username: Optional[str]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[int]
    resource_name: Optional[str]
    ip_address: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class AuditLogResponse(AuditLogSimple):
    """审计日志响应（列表用）"""
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class AuditLogDetailResponse(AuditLogResponse):
    """审计日志详情响应"""
    user_agent: Optional[str]
    changes: Optional[Dict[str, Dict[str, Any]]] = Field(None, description="变更对比")

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """审计日志列表响应（分页）"""
    items: List[AuditLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        from_attributes = True
