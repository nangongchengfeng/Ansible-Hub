from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ScriptBase(BaseModel):
    """脚本基础信息"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None)
    language: str = Field("bash", description="脚本语言: bash/python/ruby")


class ScriptCreate(ScriptBase):
    """创建脚本"""
    content: str = Field(..., description="脚本内容")
    change_description: Optional[str] = Field(None, description="变更说明")


class ScriptUpdate(BaseModel):
    """更新脚本（创建新版本）"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None)
    content: str = Field(..., description="更新内容")
    change_description: str = Field(..., description="变更说明")


class ScriptSimple(BaseModel):
    """脚本简单信息"""
    id: int
    name: str

    class Config:
        from_attributes = True


class ScriptResponse(ScriptBase):
    """脚本响应（列表用）"""
    id: int
    latest_version: Optional[int] = None
    created_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScriptVersionSimple(BaseModel):
    """脚本版本简单信息"""
    id: int
    version: int
    change_description: Optional[str] = None
    created_by: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScriptVersionDetail(BaseModel):
    """脚本版本详情"""
    id: int
    version: int
    content: str
    change_description: Optional[str] = None
    created_by: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScriptDetailResponse(ScriptBase):
    """脚本详情响应"""
    id: int
    latest_version: Optional[int] = None
    current_content: Optional[str] = None
    current_version: Optional[ScriptVersionDetail] = None
    created_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScriptVersionListResponse(BaseModel):
    """脚本版本列表响应"""
    items: List[ScriptVersionSimple]
    total: int

    class Config:
        from_attributes = True


class ScriptRollback(BaseModel):
    """回滚脚本请求"""
    target_version: int = Field(..., description="要回滚到的版本号")


class ScriptRollbackResponse(BaseModel):
    """回滚响应"""
    id: int
    latest_version: int
    rolled_back_from: int
    rolled_back_to: int

    class Config:
        from_attributes = True
