from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class CommandFilterRuleBase(BaseModel):
    """命令过滤规则基础信息"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None)
    match_type: str = Field("contains", description="匹配类型: contains/regex")
    pattern: str = Field(..., description="匹配模式")
    action: str = Field("block", description="动作: block/warn")
    priority: int = Field(0, description="优先级（数字越小优先级越高）")
    is_enabled: bool = Field(True, description="是否启用")


class CommandFilterRuleCreate(CommandFilterRuleBase):
    """创建命令过滤规则"""
    pass


class CommandFilterRuleUpdate(BaseModel):
    """更新命令过滤规则"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None)
    match_type: Optional[str] = Field(None)
    pattern: Optional[str] = Field(None)
    action: Optional[str] = Field(None)
    priority: Optional[int] = Field(None)


class CommandFilterRuleSimple(BaseModel):
    """命令过滤规则简单信息"""
    id: int
    name: str

    class Config:
        from_attributes = True


class CommandFilterRuleResponse(CommandFilterRuleBase):
    """命令过滤规则响应（列表用）"""
    id: int
    created_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CommandFilterRuleDetailResponse(CommandFilterRuleBase):
    """命令过滤规则详情响应"""
    id: int
    created_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CommandFilterRuleListResponse(BaseModel):
    """命令过滤规则列表响应"""
    total: int
    items: List[CommandFilterRuleResponse]

    class Config:
        from_attributes = True


class CommandCheckRequest(BaseModel):
    """命令检查请求"""
    command: str = Field(..., description="要检查的命令")


class MatchedRule(BaseModel):
    """匹配的规则"""
    id: int
    name: str
    action: str
    match_type: str
    pattern: str

    class Config:
        from_attributes = True


class CommandCheckResponse(BaseModel):
    """命令检查响应"""
    allowed: bool
    matched_rules: List[MatchedRule]
    severity: str
    message: str


class ReorderRulesRequest(BaseModel):
    """重新排序规则请求"""
    order: List[int] = Field(..., description="规则ID的新顺序")
