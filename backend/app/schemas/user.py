from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """用户角色枚举"""
    SUPER_ADMIN = "super_admin"
    OPERATOR = "operator"
    DEVELOPER = "developer"
    AUDITOR = "auditor"

    @classmethod
    def _missing_(cls, value):
        """兼容 superadmin 和 super_admin 两种格式"""
        if value == "superadmin":
            return cls.SUPER_ADMIN
        return super()._missing_(value)


class UserBase(BaseModel):
    """用户基础信息"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    is_active: bool = True


class UserCreate(UserBase):
    """创建用户"""
    password: str = Field(..., min_length=6, max_length=128)
    real_name: Optional[str] = Field(None, max_length=50)
    role: UserRole = UserRole.OPERATOR


class UserUpdate(BaseModel):
    """更新用户"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    real_name: Optional[str] = Field(None, max_length=50)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResetPassword(BaseModel):
    """重置密码"""
    new_password: str = Field(..., min_length=6, max_length=128)


class UserResponse(UserBase):
    """用户响应"""
    id: int
    real_name: Optional[str] = None
    role: str  # 直接用字符串
    last_login_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, v):
        """验证并转换角色值"""
        if isinstance(v, UserRole):
            v = v.value
        if v == "super_admin":
            return "superadmin"
        return v

    class Config:
        from_attributes = True


class UserSimple(BaseModel):
    """Simple user info"""
    id: int
    username: str
    real_name: Optional[str] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应"""
    total: int
    items: list[UserResponse]
