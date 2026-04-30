from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.system_user import SystemUserSimple
from app.schemas.user import UserSimple


class GatewayBase(BaseModel):
    """网关基础信息"""
    name: str = Field(..., min_length=1, max_length=100)
    ip: str = Field(..., min_length=1, max_length=45)
    port: int = Field(22, ge=1, le=65535)
    system_user_id: int


class GatewayCreate(GatewayBase):
    """创建网关"""
    pass


class GatewayUpdate(BaseModel):
    """更新网关"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    ip: Optional[str] = Field(None, min_length=1, max_length=45)
    port: Optional[int] = Field(None, ge=1, le=65535)
    system_user_id: Optional[int] = None


class GatewaySimple(BaseModel):
    """网关简单信息"""
    id: int
    name: str

    class Config:
        from_attributes = True


class GatewayResponse(GatewayBase):
    """网关响应（列表用）"""
    id: int
    system_user: Optional[SystemUserSimple] = None
    created_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GatewayListResponse(BaseModel):
    """网关列表响应"""
    total: int
    items: List[GatewayResponse]


class GatewayDetailResponse(GatewayBase):
    """网关详情响应"""
    id: int
    system_user: Optional[SystemUserSimple] = None
    created_by: int
    creator: Optional[UserSimple] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
