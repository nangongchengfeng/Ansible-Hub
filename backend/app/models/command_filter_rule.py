from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class CommandFilterRule(Base):
    """命令过滤规则模型"""
    __tablename__ = "command_filter_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="规则名称")
    description = Column(Text, nullable=True, comment="描述")
    match_type = Column(String(20), nullable=False, default="contains", comment="匹配类型: contains/regex")
    pattern = Column(Text, nullable=False, comment="匹配模式")
    action = Column(String(20), nullable=False, default="block", comment="动作: block/warn")
    priority = Column(Integer, nullable=False, default=0, comment="优先级（数字越小优先级越高）")
    is_enabled = Column(Boolean, nullable=False, default=True, comment="是否启用")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])

    @property
    def changes(self):
        """计算变更对比（占位，保持兼容性）"""
        return {}
