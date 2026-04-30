from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PlaybookBase(BaseModel):
    """剧本基础信息"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None)


class PlaybookCreate(PlaybookBase):
    """创建剧本"""
    content: str = Field(..., description="剧本内容")
    change_description: Optional[str] = Field(None, description="变更说明")


class PlaybookUpdate(BaseModel):
    """更新剧本（创建新版本）"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None)
    content: str = Field(..., description="更新内容")
    change_description: str = Field(..., description="变更说明")


class PlaybookSimple(BaseModel):
    """剧本简单信息"""
    id: int
    name: str

    class Config:
        from_attributes = True


class PlaybookResponse(PlaybookBase):
    """剧本响应（列表用）"""
    id: int
    latest_version: Optional[int] = None
    created_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PlaybookListResponse(BaseModel):
    """剧本列表响应"""
    total: int
    items: List[PlaybookResponse]


class PlaybookVersionSimple(BaseModel):
    """剧本版本简单信息"""
    id: int
    version: int
    change_description: Optional[str] = None
    created_by: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PlaybookVersionDetail(BaseModel):
    """剧本版本详情"""
    id: int
    version: int
    content: str
    change_description: Optional[str] = None
    created_by: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PlaybookDetailResponse(PlaybookBase):
    """剧本详情响应"""
    id: int
    latest_version: Optional[int] = None
    current_content: Optional[str] = None
    current_version: Optional[PlaybookVersionDetail] = None
    created_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PlaybookVersionListResponse(BaseModel):
    """剧本版本列表响应"""
    items: List[PlaybookVersionSimple]
    total: int

    class Config:
        from_attributes = True


class PlaybookRollback(BaseModel):
    """回滚剧本请求"""
    target_version: int = Field(..., description="要回滚到的版本号")


class PlaybookRollbackResponse(BaseModel):
    """回滚响应"""
    id: int
    latest_version: int
    rolled_back_from: int
    rolled_back_to: int

    class Config:
        from_attributes = True
