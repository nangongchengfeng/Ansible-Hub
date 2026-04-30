from pydantic import BaseModel, Field
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime

if TYPE_CHECKING:
    from app.schemas.business_node import BusinessNodeSimple
    from app.schemas.system_user import SystemUserSimple
    from app.schemas.gateway import GatewaySimple
    from app.schemas.user import UserSimple


class HostBase(BaseModel):
    """主机基础信息"""
    name: str = Field(..., min_length=1, max_length=100)
    business_node_id: int
    ip_internal: Optional[str] = Field(None, max_length=45)
    ip_external: Optional[str] = Field(None, max_length=45)
    ip_preference: str = Field("internal")
    ssh_port: int = Field(22, ge=1, le=65535)
    cloud_provider: Optional[str] = Field(None, max_length=50)
    system_user_id: Optional[int] = None
    gateway_id: Optional[int] = None


class HostCreate(HostBase):
    """创建主机"""
    pass


class HostUpdate(BaseModel):
    """更新主机"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    business_node_id: Optional[int] = None
    ip_internal: Optional[str] = Field(None, max_length=45)
    ip_external: Optional[str] = Field(None, max_length=45)
    ip_preference: Optional[str] = None
    ssh_port: Optional[int] = Field(None, ge=1, le=65535)
    cloud_provider: Optional[str] = Field(None, max_length=50)
    system_user_id: Optional[int] = None
    gateway_id: Optional[int] = None


class HostSimple(BaseModel):
    """主机简单信息"""
    id: int
    name: str

    class Config:
        from_attributes = True


class HostResponse(HostBase):
    """主机响应（列表用）"""
    id: int
    is_enabled: bool
    last_connection_status: Optional[str] = None
    last_connected_at: Optional[datetime] = None
    created_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HostListResponse(BaseModel):
    """主机列表响应"""
    total: int
    items: List[HostResponse]


class HostDetailResponse(HostResponse):
    """主机详情响应"""
    resolved_connection: Optional["ResolvedConnectionConfig"] = None
    business_node: Optional["BusinessNodeSimple"] = None
    system_user: Optional["SystemUserSimple"] = None
    gateway: Optional["GatewaySimple"] = None
    creator: Optional["UserSimple"] = None

    class Config:
        from_attributes = True


class HostMoveRequest(BaseModel):
    """移动主机请求"""
    target_business_node_id: int


class ResolutionPathItem(BaseModel):
    """解析路径项"""
    level: str
    field: str
    value: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class ResolvedConnectionConfig(BaseModel):
    """解析后的连接配置"""
    host_id: int
    host_name: str
    ip: Optional[str] = None
    ssh_port: int
    system_user_id: Optional[int] = None
    system_user: Optional[object] = None
    gateway_id: Optional[int] = None
    gateway: Optional[object] = None
    gateway_source: Optional[str] = None
    resolution_path: List[ResolutionPathItem] = Field(default_factory=list)
    resolved_config: Optional[dict] = None

    class Config:
        from_attributes = True


class HostConnectionConfigResponse(BaseModel):
    """主机连接配置响应"""
    config: ResolvedConnectionConfig

    class Config:
        from_attributes = True


# Rebuild models with forward references
from app.schemas.business_node import BusinessNodeSimple
from app.schemas.system_user import SystemUserSimple
from app.schemas.gateway import GatewaySimple
from app.schemas.user import UserSimple
HostDetailResponse.model_rebuild()
