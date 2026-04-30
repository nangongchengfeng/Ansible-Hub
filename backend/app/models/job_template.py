from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class JobTemplate(Base):
    """作业模板模型"""
    __tablename__ = "job_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="模板名称")
    description = Column(Text, nullable=True, comment="描述")
    job_type = Column(String(20), nullable=False, comment="作业类型：shell/module/playbook/script")

    # 作业内容（根据 job_type 不同，存储不同内容）
    shell_command = Column(Text, nullable=True, comment="Shell 命令")
    module_name = Column(String(100), nullable=True, comment="模块名称")
    module_args = Column(Text, nullable=True, comment="模块参数")
    playbook_id = Column(Integer, ForeignKey("playbooks.id"), nullable=True, comment="剧本 ID")
    playbook_version = Column(Integer, nullable=True, comment="剧本版本号")
    script_id = Column(Integer, ForeignKey("scripts.id"), nullable=True, comment="脚本 ID")
    script_version = Column(Integer, nullable=True, comment="脚本版本号")

    # 目标选择
    target_type = Column(String(20), nullable=False, comment="目标类型：host/hosts/business_node")
    target_host_ids = Column(JSON, nullable=True, comment="目标主机 ID 列表")
    target_business_node_id = Column(Integer, ForeignKey("business_nodes.id"), nullable=True, comment="目标业务节点 ID")

    # 权限相关
    business_node_id = Column(Integer, ForeignKey("business_nodes.id"), nullable=True, comment="所属业务节点")

    # 状态
    is_enabled = Column(Boolean, nullable=False, default=True, comment="是否启用")

    # 创建信息
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    playbook = relationship("Playbook", foreign_keys=[playbook_id])
    script = relationship("Script", foreign_keys=[script_id])
    target_business_node = relationship("BusinessNode", foreign_keys=[target_business_node_id])
    business_node = relationship("BusinessNode", foreign_keys=[business_node_id])
