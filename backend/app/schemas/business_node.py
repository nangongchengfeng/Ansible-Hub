from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BusinessNodeBase(BaseModel):
    """业务节点基础信息"""
    name: str = Field(..., min_length=1, max_length=100, description="节点名称")
    description: Optional[str] = Field(None, description="描述")
    parent_id: Optional[int] = Field(None, description="父节点ID")
    sort_order: int = Field(0, description="排序")
    gateway_id: Optional[int] = Field(None, description="绑定的网关ID")


class BusinessNodeCreate(BusinessNodeBase):
    """创建业务节点"""
    pass


class BusinessNodeUpdate(BaseModel):
    """更新业务节点"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    gateway_id: Optional[int] = None


class BusinessNodeSimple(BaseModel):
    """业务节点简单信息"""
    id: int
    name: str

    class Config:
        from_attributes = True


class BusinessNodeResponse(BusinessNodeBase):
    """业务节点响应"""
    id: int
    created_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BusinessNodeTreeItem(BusinessNodeResponse):
    """业务节点树状结构项"""
    children: List["BusinessNodeTreeItem"] = []

    class Config:
        from_attributes = True


BusinessNodeTreeItem.model_rebuild()
