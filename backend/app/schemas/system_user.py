from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SystemUserBase(BaseModel):
    """系统用户基础信息"""
    name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=1, max_length=100)
    auth_type: str = Field(..., description="认证类型: private_key/password")
    become_method: Optional[str] = Field("sudo", description="提权方式: sudo/su")
    become_username: Optional[str] = Field(None, max_length=100)


class SystemUserCreate(SystemUserBase):
    """创建系统用户"""
    private_key: Optional[str] = Field(None, description="私钥内容")
    password: Optional[str] = Field(None, description="密码")
    become_password: Optional[str] = Field(None, description="提权密码")


class SystemUserUpdate(BaseModel):
    """更新系统用户"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    username: Optional[str] = Field(None, min_length=1, max_length=100)
    private_key: Optional[str] = Field(None, description="更新私钥")
    password: Optional[str] = Field(None, description="更新密码")
    become_method: Optional[str] = Field(None, description="提权方式: sudo/su")
    become_username: Optional[str] = Field(None, max_length=100)
    become_password: Optional[str] = Field(None, description="更新提权密码")


class SystemUserSimple(BaseModel):
    """系统用户简单信息"""
    id: int
    name: str
    username: Optional[str] = None

    class Config:
        from_attributes = True


class SystemUserResponse(SystemUserBase):
    """系统用户响应（列表用，隐藏敏感字段）"""
    id: int
    created_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    can_view_secret: bool = False  # 标记当前用户是否能查看敏感字段

    class Config:
        from_attributes = True


class SystemUserListResponse(BaseModel):
    """系统用户列表响应"""
    total: int
    items: List[SystemUserResponse]


class SystemUserDetailResponse(SystemUserBase):
    """系统用户详情响应（可能包含敏感字段）"""
    id: int
    private_key: Optional[str] = None
    password: Optional[str] = None
    become_password: Optional[str] = None
    created_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
