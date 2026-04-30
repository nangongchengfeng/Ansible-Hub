from typing import Optional, List, Tuple
import re
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.command_filter_rule import CommandFilterRule
from app.schemas.command_filter_rule import CommandFilterRuleCreate, CommandFilterRuleUpdate


class CommandFilterRuleService:
    """命令过滤规则服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, rule_id: int) -> Optional[CommandFilterRule]:
        """通过ID获取规则"""
        result = await db.execute(
            select(CommandFilterRule)
            .where(CommandFilterRule.id == rule_id)
            .options(selectinload(CommandFilterRule.creator))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        is_enabled: Optional[bool] = None,
        match_type: Optional[str] = None,
    ) -> Tuple[int, List[CommandFilterRule]]:
        """获取规则列表"""
        # Build conditions
        conditions = []
        if is_enabled is not None:
            conditions.append(CommandFilterRule.is_enabled == is_enabled)
        if match_type:
            conditions.append(CommandFilterRule.match_type == match_type)

        # Count
        count_query = select(CommandFilterRule.id)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # Query data - ordered by priority
        data_query = select(CommandFilterRule).options(
            selectinload(CommandFilterRule.creator)
        )
        if conditions:
            data_query = data_query.where(and_(*conditions))
        data_query = data_query.order_by(CommandFilterRule.priority.asc(), CommandFilterRule.id.asc()).offset(skip).limit(limit)
        data_result = await db.execute(data_query)
        rules = list(data_result.scalars().all())

        return total, rules

    @staticmethod
    async def create(
        db: AsyncSession,
        rule_in: CommandFilterRuleCreate,
        created_by: int,
    ) -> CommandFilterRule:
        """创建规则"""
        rule = CommandFilterRule(
            name=rule_in.name,
            description=rule_in.description,
            match_type=rule_in.match_type,
            pattern=rule_in.pattern,
            action=rule_in.action,
            priority=rule_in.priority,
            is_enabled=rule_in.is_enabled,
            created_by=created_by,
        )
        db.add(rule)
        await db.commit()
        await db.refresh(rule)

        # Load relationships
        result = await db.execute(
            select(CommandFilterRule)
            .where(CommandFilterRule.id == rule.id)
            .options(selectinload(CommandFilterRule.creator))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update(
        db: AsyncSession,
        rule: CommandFilterRule,
        rule_in: CommandFilterRuleUpdate,
    ) -> CommandFilterRule:
        """更新规则"""
        update_data = rule_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)

        await db.commit()
        await db.refresh(rule)

        # Load relationships
        result = await db.execute(
            select(CommandFilterRule)
            .where(CommandFilterRule.id == rule.id)
            .options(selectinload(CommandFilterRule.creator))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def toggle(
        db: AsyncSession,
        rule: CommandFilterRule,
    ) -> CommandFilterRule:
        """切换启用/禁用状态"""
        rule.is_enabled = not rule.is_enabled
        await db.commit()
        await db.refresh(rule)
        return rule

    @staticmethod
    async def reorder(
        db: AsyncSession,
        order: List[int],
    ):
        """重新排序规则"""
        # Get all rules in the new order
        for index, rule_id in enumerate(order):
            rule = await CommandFilterRuleService.get_by_id(db, rule_id)
            if rule:
                rule.priority = index

        await db.commit()

    @staticmethod
    async def delete(db: AsyncSession, rule: CommandFilterRule):
        """删除规则"""
        await db.delete(rule)
        await db.commit()

    @staticmethod
    async def check_command(
        db: AsyncSession,
        command: str,
    ) -> Tuple[bool, List[CommandFilterRule], str]:
        """检查命令是否匹配规则"""
        # Get all enabled rules, ordered by priority
        result = await db.execute(
            select(CommandFilterRule)
            .where(CommandFilterRule.is_enabled == True)
            .order_by(CommandFilterRule.priority.asc(), CommandFilterRule.id.asc())
        )
        rules = list(result.scalars().all())

        matched_rules = []
        final_action = "warn"

        for rule in rules:
            matched = False
            if rule.match_type == "contains":
                matched = rule.pattern in command
            elif rule.match_type == "regex":
                try:
                    matched = bool(re.search(rule.pattern, command))
                except re.error:
                    # Skip invalid regex patterns
                    continue

            if matched:
                matched_rules.append(rule)
                if rule.action == "block":
                    final_action = "block"
                elif final_action != "block" and rule.action == "warn":
                    final_action = "warn"

        allowed = final_action != "block"
        return allowed, matched_rules, final_action
