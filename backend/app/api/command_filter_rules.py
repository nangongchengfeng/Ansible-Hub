from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_superuser
from app.models.user import User
from app.models.command_filter_rule import CommandFilterRule, MatchType, ActionType
from app.schemas.command_filter_rule import (
    CommandFilterRuleCreate,
    CommandFilterRuleUpdate,
    CommandFilterRuleResponse,
    CommandFilterRuleListResponse,
    CommandFilterRuleDetailResponse,
    CommandCheckRequest,
    CommandCheckResponse,
    ReorderRulesRequest,
)
from app.services.command_filter_rule import CommandFilterRuleService

router = APIRouter(prefix="/command-filter-rules", tags=["命令过滤规则"])


@router.get("", response_model=CommandFilterRuleListResponse)
async def get_command_filter_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_enabled: Optional[bool] = Query(None),
    match_type: Optional[MatchType] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取命令过滤规则列表"""
    total, rules = await CommandFilterRuleService.get_list(
        db=db, skip=skip, limit=limit, is_enabled=is_enabled, match_type=match_type
    )
    return CommandFilterRuleListResponse(total=total, items=rules)


@router.post("", response_model=CommandFilterRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_command_filter_rule(
    rule_in: CommandFilterRuleCreate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """创建命令过滤规则"""
    rule = await CommandFilterRuleService.create(
        db=db, rule_in=rule_in, created_by=current_user.id
    )
    return rule


@router.get("/{rule_id}", response_model=CommandFilterRuleDetailResponse)
async def get_command_filter_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取命令过滤规则详情"""
    rule = await CommandFilterRuleService.get_by_id(db, rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="规则不存在"
        )
    return rule


@router.put("/{rule_id}", response_model=CommandFilterRuleResponse)
async def update_command_filter_rule(
    rule_id: int,
    rule_in: CommandFilterRuleUpdate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """更新命令过滤规则"""
    rule = await CommandFilterRuleService.get_by_id(db, rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="规则不存在"
        )

    rule = await CommandFilterRuleService.update(db, rule, rule_in)
    return rule


@router.patch("/{rule_id}/toggle", response_model=CommandFilterRuleResponse)
async def toggle_command_filter_rule(
    rule_id: int,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """切换命令过滤规则启用/禁用状态"""
    rule = await CommandFilterRuleService.get_by_id(db, rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="规则不存在"
        )

    rule = await CommandFilterRuleService.toggle(db, rule)
    return rule


@router.put("/reorder", status_code=status.HTTP_200_OK)
async def reorder_command_filter_rules(
    reorder_in: ReorderRulesRequest,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """重新排序命令过滤规则"""
    await CommandFilterRuleService.reorder(db, reorder_in.order)
    return {"success": True, "message": "规则排序更新成功"}


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_command_filter_rule(
    rule_id: int,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """删除命令过滤规则"""
    rule = await CommandFilterRuleService.get_by_id(db, rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="规则不存在"
        )
    await CommandFilterRuleService.delete(db, rule)
    return None


@router.post("/check", response_model=CommandCheckResponse)
async def check_command(
    check_in: CommandCheckRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """检查命令是否被过滤"""
    allowed, matched_rules, severity = await CommandFilterRuleService.check_command(db, check_in.command)

    message = "命令允许执行"
    if severity == ActionType.WARN:
        message = "命令有警告但允许执行"
    elif severity == ActionType.BLOCK:
        message = "命令被禁止"

    return CommandCheckResponse(
        allowed=allowed,
        matched_rules=matched_rules,
        severity=severity,
        message=message
    )
