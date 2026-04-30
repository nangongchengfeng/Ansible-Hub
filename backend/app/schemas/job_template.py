from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any, Dict
from datetime import datetime
from enum import Enum


class TargetType(str, Enum):
    HOST = "host"
    HOSTS = "hosts"
    BUSINESS_NODE = "business_node"


class JobTemplateBase(BaseModel):
    """作业模板基础信息"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None)
    job_type: str = Field(..., description="作业类型：shell/module/playbook/script")

    # 作业内容
    shell_command: Optional[str] = Field(None, description="Shell 命令")
    module_name: Optional[str] = Field(None, description="模块名称")
    module_args: Optional[str] = Field(None, description="模块参数")
    playbook_id: Optional[int] = Field(None, description="剧本 ID")
    playbook_version: Optional[int] = Field(None, description="剧本版本号")
    script_id: Optional[int] = Field(None, description="脚本 ID")
    script_version: Optional[int] = Field(None, description="脚本版本号")

    # 目标选择
    target_type: TargetType = Field(..., description="目标类型")
    target_host_id: Optional[int] = Field(None, description="单个主机 ID（target_type=host）")
    target_host_ids: Optional[List[int]] = Field(None, description="多个主机 ID 列表（target_type=hosts）")
    target_business_node_id: Optional[int] = Field(None, description="业务节点 ID（target_type=business_node）")

    # 权限相关
    business_node_id: Optional[int] = Field(None, description="所属业务节点")

    # 状态
    is_enabled: bool = Field(True, description="是否启用")

    @field_validator('shell_command', 'module_name', 'playbook_id', 'script_id')
    @classmethod
    def validate_job_type_fields(cls, v, info):
        """验证作业类型对应的字段"""
        job_type = info.data.get('job_type')
        field_name = info.field_name

        if job_type == 'shell' and field_name == 'shell_command' and not v:
            raise ValueError('shell_command is required when job_type is shell')
        if job_type == 'module' and field_name == 'module_name' and not v:
            raise ValueError('module_name is required when job_type is module')
        if job_type == 'playbook' and field_name == 'playbook_id' and not v:
            raise ValueError('playbook_id is required when job_type is playbook')
        if job_type == 'script' and field_name == 'script_id' and not v:
            raise ValueError('script_id is required when job_type is script')

        return v

    @field_validator('target_host_id', 'target_host_ids', 'target_business_node_id')
    @classmethod
    def validate_target_fields(cls, v, info):
        """验证目标字段"""
        target_type = info.data.get('target_type')
        field_name = info.field_name

        if target_type == TargetType.HOST and field_name == 'target_host_id' and not v:
            raise ValueError('target_host_id is required when target_type is host')
        if target_type == TargetType.HOSTS and field_name == 'target_host_ids' and not v:
            raise ValueError('target_host_ids is required when target_type is hosts')
        if target_type == TargetType.BUSINESS_NODE and field_name == 'target_business_node_id' and not v:
            raise ValueError('target_business_node_id is required when target_type is business_node')

        return v


class JobTemplateCreate(JobTemplateBase):
    """创建作业模板"""
    pass


class JobTemplateUpdate(BaseModel):
    """更新作业模板"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None)
    job_type: Optional[str] = Field(None)
    shell_command: Optional[str] = Field(None)
    module_name: Optional[str] = Field(None)
    module_args: Optional[str] = Field(None)
    playbook_id: Optional[int] = Field(None)
    playbook_version: Optional[int] = Field(None)
    script_id: Optional[int] = Field(None)
    script_version: Optional[int] = Field(None)
    target_type: Optional[TargetType] = Field(None)
    target_host_id: Optional[int] = Field(None)
    target_host_ids: Optional[List[int]] = Field(None)
    target_business_node_id: Optional[int] = Field(None)
    business_node_id: Optional[int] = Field(None)
    is_enabled: Optional[bool] = Field(None)


class JobTemplateSimple(BaseModel):
    """作业模板简单信息"""
    id: int
    name: str
    job_type: str
    is_enabled: bool

    class Config:
        from_attributes = True


class JobTemplateResponse(JobTemplateBase):
    """作业模板响应（列表用）"""
    id: int
    created_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobTemplateDetailResponse(JobTemplateBase):
    """作业模板详情响应"""
    id: int
    created_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobTemplateListResponse(BaseModel):
    """作业模板列表响应"""
    total: int
    items: List[JobTemplateResponse]


class JobTemplateExecute(BaseModel):
    """执行作业模板请求（支持覆盖参数）"""
    # 可覆盖的字段
    shell_command: Optional[str] = Field(None)
    module_name: Optional[str] = Field(None)
    module_args: Optional[str] = Field(None)
    playbook_id: Optional[int] = Field(None)
    playbook_version: Optional[int] = Field(None)
    script_id: Optional[int] = Field(None)
    script_version: Optional[int] = Field(None)
    target_type: Optional[TargetType] = Field(None)
    target_host_id: Optional[int] = Field(None)
    target_host_ids: Optional[List[int]] = Field(None)
    target_business_node_id: Optional[int] = Field(None)


class SaveTemplateFromJob(BaseModel):
    """从历史作业保存为模板请求"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None)
    business_node_id: Optional[int] = Field(None)
