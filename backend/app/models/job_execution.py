from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.core.database import Base


class JobType(str, Enum):
    """作业类型枚举"""
    SHELL = "shell"
    MODULE = "module"
    PLAYBOOK = "playbook"
    SCRIPT = "script"


class JobStatus(str, Enum):
    """作业状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class JobExecution(Base):
    """作业执行模型"""
    __tablename__ = "job_executions"

    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String(20), nullable=False, comment="作业类型: shell/module/playbook/script")

    # 作业内容（根据job_type不同，存储不同内容）
    shell_command = Column(Text, nullable=True, comment="Shell命令")
    module_name = Column(String(100), nullable=True, comment="模块名称")
    module_args = Column(Text, nullable=True, comment="模块参数")
    playbook_id = Column(Integer, ForeignKey("playbooks.id"), nullable=True, comment="剧本ID")
    playbook_version = Column(Integer, nullable=True, comment="剧本版本号")
    script_id = Column(Integer, ForeignKey("scripts.id"), nullable=True, comment="脚本ID")
    script_version = Column(Integer, nullable=True, comment="脚本版本号")

    # 目标选择
    target_type = Column(String(20), nullable=False, comment="目标类型: host/hosts/business_node")
    target_host_ids = Column(JSON, nullable=True, comment="目标主机ID列表")
    target_business_node_id = Column(Integer, ForeignKey("business_nodes.id"), nullable=True, comment="目标业务节点ID")

    # 状态
    status = Column(String(20), nullable=False, default="pending", comment="状态: pending/running/completed/failed/cancelled")
    started_at = Column(DateTime(timezone=True), nullable=True, comment="开始时间")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="完成时间")

    # 命令过滤检查结果
    command_check_passed = Column(Boolean, nullable=True, comment="命令检查是否通过")
    command_check_result = Column(JSON, nullable=True, comment="命令检查详细结果")

    # 错误信息
    error_message = Column(Text, nullable=True, comment="错误信息")

    # 创建信息
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    playbook = relationship("Playbook", foreign_keys=[playbook_id])
    script = relationship("Script", foreign_keys=[script_id])
    target_business_node = relationship("BusinessNode", foreign_keys=[target_business_node_id])
    tasks = relationship("Task", back_populates="job_execution", cascade="all, delete-orphan", order_by="Task.id")


class Task(Base):
    """任务模型（对应单个主机的执行）"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    job_execution_id = Column(Integer, ForeignKey("job_executions.id", ondelete="CASCADE"), nullable=False)
    host_id = Column(Integer, ForeignKey("hosts.id"), nullable=False)

    # 连接配置（快照，防止后续配置变更影响结果展示）
    connection_config = Column(JSON, nullable=True, comment="连接配置快照")

    # 执行状态
    status = Column(String(20), nullable=False, default="pending", comment="状态: pending/running/completed/failed/skipped")
    started_at = Column(DateTime(timezone=True), nullable=True, comment="开始时间")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="完成时间")

    # 执行结果
    stdout = Column(Text, nullable=True, comment="标准输出")
    stderr = Column(Text, nullable=True, comment="错误输出")
    result_json = Column(JSON, nullable=True, comment="完整结果JSON")
    exit_code = Column(Integer, nullable=True, comment="退出码")

    # 错误信息
    error_message = Column(Text, nullable=True, comment="错误信息")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    job_execution = relationship("JobExecution", back_populates="tasks")
    host = relationship("Host", foreign_keys=[host_id])
