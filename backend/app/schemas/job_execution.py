from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any, Dict
from datetime import datetime
from enum import Enum
from app.models.job_execution import JobType, JobStatus, TaskStatus
from app.schemas.command_filter_rule import CommandCheckResponse


# ============== 目标选择相关 ==============
class TargetType(str, Enum):
    HOST = "host"
    HOSTS = "hosts"
    BUSINESS_NODE = "business_node"


class TargetHostRequest(BaseModel):
    """单个主机目标"""
    host_id: int


class TargetHostsRequest(BaseModel):
    """多个主机目标"""
    host_ids: List[int] = Field(..., min_length=1)


class TargetBusinessNodeRequest(BaseModel):
    """业务节点目标"""
    business_node_id: int


# ============== 作业内容请求 ==============
class ShellJobRequest(BaseModel):
    """Shell命令作业"""
    job_type: JobType = JobType.SHELL
    command: str = Field(..., description="Shell命令")


class ModuleJobRequest(BaseModel):
    """Ansible模块作业"""
    job_type: JobType = JobType.MODULE
    module_name: str = Field(..., description="模块名称")
    module_args: Optional[str] = Field(None, description="模块参数")


class PlaybookJobRequest(BaseModel):
    """Ansible剧本作业"""
    job_type: JobType = JobType.PLAYBOOK
    playbook_id: int = Field(..., description="剧本ID")
    playbook_version: Optional[int] = Field(None, description="剧本版本，不传则用最新版本")


class ScriptJobRequest(BaseModel):
    """脚本作业"""
    job_type: JobType = JobType.SCRIPT
    script_id: int = Field(..., description="脚本ID")
    script_version: Optional[int] = Field(None, description="脚本版本，不传则用最新版本")


# ============== 组合请求 ==============
class JobExecutionCreate(BaseModel):
    """提交作业执行请求"""
    # 作业内容（根据类型选择对应的字段）
    job_type: JobType

    # 不同类型的内容
    shell_command: Optional[str] = Field(None, description="Shell命令（job_type=SHELL时必填）")
    module_name: Optional[str] = Field(None, description="模块名称（job_type=MODULE时必填）")
    module_args: Optional[str] = Field(None, description="模块参数")
    playbook_id: Optional[int] = Field(None, description="剧本ID（job_type=PLAYBOOK时必填）")
    playbook_version: Optional[int] = Field(None, description="剧本版本")
    script_id: Optional[int] = Field(None, description="脚本ID（job_type=SCRIPT时必填）")
    script_version: Optional[int] = Field(None, description="脚本版本")

    # 目标选择
    target_type: TargetType
    target_host_id: Optional[int] = Field(None, description="单个主机ID（target_type=host时）")
    target_host_ids: Optional[List[int]] = Field(None, description="多个主机ID（target_type=hosts时）")
    target_business_node_id: Optional[int] = Field(None, description="业务节点ID（target_type=business_node时）")

    @field_validator('shell_command')
    @classmethod
    def validate_shell_command(cls, v, info):
        if info.data.get('job_type') == JobType.SHELL and not v:
            raise ValueError('shell_command is required when job_type is SHELL')
        return v

    @field_validator('module_name')
    @classmethod
    def validate_module_name(cls, v, info):
        if info.data.get('job_type') == JobType.MODULE and not v:
            raise ValueError('module_name is required when job_type is MODULE')
        return v

    @field_validator('playbook_id')
    @classmethod
    def validate_playbook_id(cls, v, info):
        if info.data.get('job_type') == JobType.PLAYBOOK and not v:
            raise ValueError('playbook_id is required when job_type is PLAYBOOK')
        return v

    @field_validator('script_id')
    @classmethod
    def validate_script_id(cls, v, info):
        if info.data.get('job_type') == JobType.SCRIPT and not v:
            raise ValueError('script_id is required when job_type is SCRIPT')
        return v

    @field_validator('target_host_id', 'target_host_ids', 'target_business_node_id')
    @classmethod
    def validate_target(cls, v, info):
        target_type = info.data.get('target_type')
        field_name = info.field_name
        if target_type == TargetType.HOST and field_name == 'target_host_id' and not v:
            raise ValueError('target_host_id is required when target_type is host')
        if target_type == TargetType.HOSTS and field_name == 'target_host_ids' and not v:
            raise ValueError('target_host_ids is required when target_type is hosts')
        if target_type == TargetType.BUSINESS_NODE and field_name == 'target_business_node_id' and not v:
            raise ValueError('target_business_node_id is required when target_type is business_node')
        return v


# ============== 响应模型 ==============
class TaskSimple(BaseModel):
    """任务简单信息"""
    id: int
    host_id: int
    status: TaskStatus

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    """任务响应"""
    id: int
    job_execution_id: int
    host_id: int
    status: TaskStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    exit_code: Optional[int] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskDetailResponse(TaskResponse):
    """任务详情（包含结果JSON）"""
    connection_config: Optional[Dict[str, Any]] = None
    result_json: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class JobExecutionSimple(BaseModel):
    """作业执行简单信息"""
    id: int
    job_type: JobType
    status: JobStatus

    class Config:
        from_attributes = True


class JobExecutionResponse(BaseModel):
    """作业执行响应（列表用）"""
    id: int
    job_type: JobType
    status: JobStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    command_check_passed: Optional[bool] = None
    error_message: Optional[str] = None
    created_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobExecutionDetailResponse(JobExecutionResponse):
    """作业执行详情"""
    # 作业内容
    shell_command: Optional[str] = None
    module_name: Optional[str] = None
    module_args: Optional[str] = None
    playbook_id: Optional[int] = None
    playbook_version: Optional[int] = None
    script_id: Optional[int] = None
    script_version: Optional[int] = None

    # 目标信息
    target_type: str
    target_host_ids: Optional[List[int]] = None
    target_business_node_id: Optional[int] = None

    # 命令检查结果
    command_check_result: Optional[CommandCheckResponse] = None

    # 任务列表
    tasks: List[TaskResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class JobExecutionSubmitResponse(BaseModel):
    """作业提交响应"""
    id: int
    status: JobStatus
    command_check_passed: bool
    command_check_result: CommandCheckResponse
    message: str

    class Config:
        from_attributes = True


class JobExecutionListResponse(BaseModel):
    """作业执行列表响应"""
    total: int
    items: List[JobExecutionResponse]


class TaskListResponse(BaseModel):
    """任务列表响应"""
    total: int
    items: List[TaskResponse]
