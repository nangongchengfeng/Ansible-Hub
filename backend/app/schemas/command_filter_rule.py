from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.command_filter_rule import MatchType, ActionType


class CommandFilterRuleBase(BaseModel):
    """命令过滤规则基础信息"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None)
    match_type: MatchType = Field(MatchType.CONTAINS, description="匹配类型")
    pattern: str = Field(..., description="匹配模式")
    action: ActionType = Field(ActionType.BLOCK, description="动作")
    priority: int = Field(0, description="优先级（数字越小优先级越高）")
    is_enabled: bool = Field(True, description="是否启用")


class CommandFilterRuleCreate(CommandFilterRuleBase):
    """创建命令过滤规则"""
    pass


class CommandFilterRuleUpdate(BaseModel):
    """更新命令过滤规则"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None)
    match_type: Optional[MatchType] = Field(None)
    pattern: Optional[str] = Field(None)
    action: Optional[ActionType] = Field(None)
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


class CommandCheckRequest(BaseModel):
    """命令检查请求"""
    command: str = Field(..., description="要检查的命令")


class MatchedRule(BaseModel):
    """匹配的规则"""
    id: int
    name: str
    action: ActionType
    match_type: MatchType
    pattern: str

    class Config:
        from_attributes = True


class CommandCheckResponse(BaseModel):
    """命令检查响应"""
    allowed: bool
    matched_rules: List[MatchedRule]
    severity: ActionType
    message: str


class ReorderRulesRequest(BaseModel):
    """重新排序规则请求"""
    order: List[int] = Field(..., description="规则ID的新顺序")
