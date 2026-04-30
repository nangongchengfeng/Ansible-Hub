from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.websocket_manager import manager
from app.api.deps import get_current_user
from app.models.user import User
from app.models.job_execution import JobType, JobStatus
from app.schemas.job_execution import (
    JobExecutionCreate,
    JobExecutionResponse,
    JobExecutionDetailResponse,
    JobExecutionSubmitResponse,
    JobExecutionListResponse,
    TaskResponse,
    TaskDetailResponse,
    TaskListResponse,
)
from app.services.job_execution import JobExecutionService
from app.services.audit_log import audit_log

router = APIRouter(prefix="/job-executions", tags=["作业执行"])


@router.get("", response_model=JobExecutionListResponse)
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    job_type: Optional[JobType] = Query(None),
    status: Optional[JobStatus] = Query(None),
    created_by: Optional[int] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取作业列表"""
    job_type_str = job_type.value if job_type else None
    status_str = status.value if status else None

    total, jobs = await JobExecutionService.get_list(
        db=db,
        skip=skip,
        limit=limit,
        job_type=job_type_str,
        status=status_str,
        created_by=created_by,
        start_time=start_time,
        end_time=end_time,
        search=search
    )
    return JobExecutionListResponse(total=total, items=jobs)


@router.post("", response_model=JobExecutionSubmitResponse, status_code=status.HTTP_201_CREATED)
@audit_log(
    action="create",
    resource_type="job_execution",
    get_resource_id=lambda r: r.id if hasattr(r, 'id') else None,
    get_resource_name=lambda r: f"Job {r.job_type.value}" if hasattr(r, 'job_type') else None,
)
async def submit_job(
    job_in: JobExecutionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """提交作业执行"""
    try:
        job, command_check_result = await JobExecutionService.create(
            db=db, job_in=job_in, created_by=current_user.id
        )

        message = "Job submitted successfully"
        if not command_check_result.get("allowed", False):
            message = "Job blocked by command filter rules"

        return JobExecutionSubmitResponse(
            id=job.id,
            status=job.status,
            command_check_passed=command_check_result.get("allowed", False),
            command_check_result=command_check_result,
            message=message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{job_id}", response_model=JobExecutionDetailResponse)
async def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取作业详情"""
    job = await JobExecutionService.get_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作业不存在"
        )
    return job


@router.get("/{job_id}/tasks", response_model=TaskListResponse)
async def get_job_tasks(
    job_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取作业的任务列表"""
    # Check if job exists
    job = await JobExecutionService.get_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作业不存在"
        )

    total, tasks = await JobExecutionService.get_tasks_by_job_id(
        db=db, job_id=job_id, skip=skip, limit=limit
    )
    return TaskListResponse(total=total, items=tasks)


@router.get("/tasks/{task_id}", response_model=TaskDetailResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取任务详情"""
    task = await JobExecutionService.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    return task


@router.websocket("/{job_id}/output")
async def websocket_job_output(websocket: WebSocket, job_id: int):
    """WebSocket 端点：实时获取作业输出"""
    await manager.connect(job_id, websocket)
    try:
        # Keep the connection alive by listening for pings
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(job_id, websocket)


@router.get("/{job_id}/logs")
async def get_job_logs(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取作业完整日志"""
    try:
        logs = await JobExecutionService.get_job_logs(db, job_id)
        return logs
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{job_id}/cancel")
@audit_log(
    action="cancel",
    resource_type="job_execution",
    get_resource_id=lambda r, **kwargs: kwargs.get("job_id"),
    get_resource_name=lambda r, **kwargs: f"Job {kwargs.get('job_id')} cancelled",
)
async def cancel_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """取消作业"""
    try:
        job = await JobExecutionService.cancel_job(db, job_id, current_user)
        return {
            "id": job.id,
            "status": job.status,
            "message": "Job cancelled successfully"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
