from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.job_template import (
    JobTemplateCreate,
    JobTemplateUpdate,
    JobTemplateResponse,
    JobTemplateDetailResponse,
    JobTemplateListResponse,
    JobTemplateExecute,
    SaveTemplateFromJob,
)
from app.schemas.job_execution import JobExecutionSubmitResponse
from app.services.job_template import JobTemplateService
from app.services.job_execution import JobExecutionService
from app.services.audit_log import audit_log


router = APIRouter(prefix="/job-templates", tags=["作业模板"])


@router.get("", response_model=JobTemplateListResponse)
async def get_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    job_type: Optional[str] = Query(None),
    is_enabled: Optional[bool] = Query(None),
    created_by: Optional[int] = Query(None),
    business_node_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取作业模板列表"""
    total, templates = await JobTemplateService.get_list(
        db=db,
        skip=skip,
        limit=limit,
        job_type=job_type,
        is_enabled=is_enabled,
        created_by=created_by,
        business_node_id=business_node_id,
        search=search,
    )
    return JobTemplateListResponse(total=total, items=templates)


@router.post("", response_model=JobTemplateResponse, status_code=status.HTTP_201_CREATED)
@audit_log(
    action="create",
    resource_type="job_template",
    get_resource_id=lambda r: r.id if hasattr(r, 'id') else None,
    get_resource_name=lambda r: r.name if hasattr(r, 'name') else None,
)
async def create_template(
    template_in: JobTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建作业模板"""
    template = await JobTemplateService.create(
        db=db,
        template_in=template_in,
        created_by=current_user.id,
    )
    return template


@router.get("/{template_id}", response_model=JobTemplateDetailResponse)
async def get_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取作业模板详情"""
    template = await JobTemplateService.get_by_id(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作业模板不存在",
        )
    return template


@router.put("/{template_id}", response_model=JobTemplateResponse)
@audit_log(
    action="update",
    resource_type="job_template",
    get_resource_id=lambda r, **kwargs: kwargs.get("template_id"),
    get_resource_name=lambda r: r.name if hasattr(r, 'name') else None,
)
async def update_template(
    template_id: int,
    template_in: JobTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新作业模板"""
    template = await JobTemplateService.get_by_id(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作业模板不存在",
        )

    # Check permissions: creator or super_admin
    if current_user.role != "super_admin" and template.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限更新此作业模板",
        )

    template = await JobTemplateService.update(db, template, template_in)
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
@audit_log(
    action="delete",
    resource_type="job_template",
    get_resource_id=lambda r, **kwargs: kwargs.get("template_id"),
    get_resource_name=lambda r, **kwargs: f"Job Template {kwargs.get('template_id')}",
)
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除作业模板"""
    template = await JobTemplateService.get_by_id(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作业模板不存在",
        )

    # Check permissions: creator or super_admin
    if current_user.role != "super_admin" and template.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除此作业模板",
        )

    await JobTemplateService.delete(db, template)
    return None


@router.post("/{template_id}/execute", response_model=JobExecutionSubmitResponse, status_code=status.HTTP_201_CREATED)
@audit_log(
    action="execute",
    resource_type="job_template",
    get_resource_id=lambda r, **kwargs: kwargs.get("template_id"),
    get_resource_name=lambda r, **kwargs: f"Execute Job Template {kwargs.get('template_id')}",
)
async def execute_template(
    template_id: int,
    execute_in: Optional[JobTemplateExecute] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """执行作业模板（支持覆盖参数）"""
    template = await JobTemplateService.get_by_id(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作业模板不存在",
        )

    if not template.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="作业模板已禁用",
        )

    try:
        job, check_result = await JobTemplateService.execute(
            db=db,
            template=template,
            execute_in=execute_in,
            created_by=current_user.id,
        )

        message = "作业已提交"
        if not check_result.get("allowed", False):
            message = "作业被命令过滤规则阻止"

        return JobExecutionSubmitResponse(
            id=job.id,
            status=job.status,
            command_check_passed=check_result.get("allowed", False),
            command_check_result=check_result,
            message=message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/job-executions/{job_id}/save-template", response_model=JobTemplateResponse, status_code=status.HTTP_201_CREATED)
@audit_log(
    action="save_as_template",
    resource_type="job_execution",
    get_resource_id=lambda r, **kwargs: kwargs.get("job_id"),
    get_resource_name=lambda r: r.name if hasattr(r, 'name') else None,
)
async def save_template_from_job(
    job_id: int,
    save_in: SaveTemplateFromJob,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """从历史作业保存为模板"""
    job = await JobExecutionService.get_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作业不存在",
        )

    try:
        template = await JobTemplateService.save_from_job(
            db=db,
            job=job,
            save_in=save_in,
            created_by=current_user.id,
        )
        return template
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
