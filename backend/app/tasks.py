"""Celery任务模块"""
from typing import Dict, Any
from datetime import datetime
from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal as async_session_maker
from app.core.job_events import (
    sync_publish_job_event, JobEventChannels
)
from app.models.job_execution import JobExecution, Task
from sqlalchemy import select
from sqlalchemy.orm import selectinload


def sync_update_job_status(job_id: int, status: str, started_at=None, completed_at=None, error_message=None):
    """同步更新作业状态（用于Celery任务）"""
    import asyncio

    async def _update():
        async with async_session_maker() as session:
            result = await session.execute(
                select(JobExecution).where(JobExecution.id == job_id)
            )
            job = result.scalar_one_or_none()
            if job:
                job.status = status
                if started_at:
                    job.started_at = started_at
                if completed_at:
                    job.completed_at = completed_at
                if error_message:
                    job.error_message = error_message
                job.updated_at = datetime.utcnow()
                await session.commit()

    asyncio.run(_update())


def sync_update_task_status(task_id: int, status: str, started_at=None, completed_at=None,
                            stdout=None, stderr=None, result_json=None, exit_code=None, error_message=None):
    """同步更新任务状态"""
    import asyncio

    async def _update():
        async with async_session_maker() as session:
            result = await session.execute(
                select(Task).where(Task.id == task_id)
            )
            task = result.scalar_one_or_none()
            if task:
                task.status = status
                if started_at:
                    task.started_at = started_at
                if completed_at:
                    task.completed_at = completed_at
                if stdout is not None:
                    task.stdout = stdout
                if stderr is not None:
                    task.stderr = stderr
                if result_json is not None:
                    task.result_json = result_json
                if exit_code is not None:
                    task.exit_code = exit_code
                if error_message is not None:
                    task.error_message = error_message
                task.updated_at = datetime.utcnow()
                await session.commit()

    asyncio.run(_update())


def sync_get_job(job_id: int) -> Dict[str, Any]:
    """同步获取作业信息"""
    import asyncio

    async def _get():
        async with async_session_maker() as session:
            result = await session.execute(
                select(JobExecution)
                .where(JobExecution.id == job_id)
                .options(selectinload(JobExecution.tasks))
            )
            job = result.scalar_one_or_none()
            if not job:
                return None

            # Get script content if needed
            script_content = None
            if job.job_type == "script" and job.script_id:
                from app.models.script import Script
                script_result = await session.execute(
                    select(Script)
                    .where(Script.id == job.script_id)
                    .options(selectinload(Script.versions))
                )
                script = script_result.scalar_one_or_none()
                if script and script.versions:
                    # Find the right version
                    target_version = job.script_version
                    if not target_version:
                        target_version = script.latest_version
                    for v in script.versions:
                        if v.version == target_version:
                            script_content = v.content
                            break

            # Get playbook content if needed
            playbook_content = None
            if job.job_type == "playbook" and job.playbook_id:
                from app.models.playbook import Playbook
                playbook_result = await session.execute(
                    select(Playbook)
                    .where(Playbook.id == job.playbook_id)
                    .options(selectinload(Playbook.versions))
                )
                playbook = playbook_result.scalar_one_or_none()
                if playbook and playbook.versions:
                    target_version = job.playbook_version
                    if not target_version:
                        target_version = playbook.latest_version
                    for v in playbook.versions:
                        if v.version == target_version:
                            playbook_content = v.content
                            break

            return {
                "id": job.id,
                "job_type": job.job_type,
                "shell_command": job.shell_command,
                "module_name": job.module_name,
                "module_args": job.module_args,
                "script_id": job.script_id,
                "script_content": script_content,
                "playbook_id": job.playbook_id,
                "playbook_content": playbook_content,
                "tasks": [
                    {
                        "id": t.id,
                        "host_id": t.host_id,
                        "connection_config": t.connection_config
                    }
                    for t in job.tasks
                ]
            }

    return asyncio.run(_get())


def sync_check_job_cancelled(job_id: int) -> bool:
    """检查作业是否被取消"""
    import asyncio

    async def _check():
        async with async_session_maker() as session:
            result = await session.execute(
                select(JobExecution).where(JobExecution.id == job_id)
            )
            job = result.scalar_one_or_none()
            return job is not None and job.status == "cancelled"

    return asyncio.run(_check())


@celery_app.task(bind=True)
def execute_job(self, job_id: int):
    """执行作业"""
    from datetime import datetime

    # Update job status to running
    sync_update_job_status(job_id, "running", started_at=datetime.utcnow())
    sync_publish_job_event(
        JobEventChannels.JOB_STATUS,
        {"job_id": job_id, "status": "running"}
    )

    try:
        # Get job data
        job_data = sync_get_job(job_id)
        if not job_data:
            sync_update_job_status(
                job_id,
                "failed",
                completed_at=datetime.utcnow(),
                error_message="Job not found"
            )
            sync_publish_job_event(
                JobEventChannels.JOB_COMPLETE,
                {"job_id": job_id, "status": "failed", "success": False}
            )
            return {"success": False, "error": "Job not found"}

        # Process each task
        all_success = True
        for task_data in job_data["tasks"]:
            # Check if job is cancelled
            if sync_check_job_cancelled(job_id):
                # Update remaining tasks as skipped
                sync_update_task_status(task_data["id"], "skipped")
                continue

            task_id = task_data["id"]
            connection_config = task_data.get("connection_config", {})

            # Update task status to running
            sync_update_task_status(task_id, "running", started_at=datetime.utcnow())
            sync_publish_job_event(
                JobEventChannels.JOB_STATUS,
                {"job_id": job_id, "status": "running", "extra": {"task_id": task_id}}
            )

            try:
                # Prepare hosts data
                hosts_data = [connection_config]

                # Execute based on job type
                stdout = ""
                stderr = ""
                exit_code = 0
                success = True

                if job_data["job_type"] == "shell":
                    # For shell command, we'll just simulate for now
                    # In real implementation, use ansible_runner_wrapper
                    stdout = f"Executed: {job_data['shell_command']}\n(Not implemented - this is a simulation)"
                    stderr = ""
                    exit_code = 0
                    success = True
                elif job_data["job_type"] == "module":
                    stdout = f"Module: {job_data['module_name']} Args: {job_data['module_args']}\n(Not implemented - this is a simulation)"
                    stderr = ""
                    exit_code = 0
                    success = True
                elif job_data["job_type"] == "script":
                    stdout = f"Script ID: {job_data['script_id']}\nContent: {job_data['script_content'][:100]}...\n(Not implemented - this is a simulation)"
                    stderr = ""
                    exit_code = 0
                    success = True
                elif job_data["job_type"] == "playbook":
                    stdout = f"Playbook ID: {job_data['playbook_id']}\nContent: {job_data['playbook_content'][:100]}...\n(Not implemented - this is a simulation)"
                    stderr = ""
                    exit_code = 0
                    success = True

                # Publish task output
                sync_publish_job_event(
                    JobEventChannels.TASK_OUTPUT,
                    {"job_id": job_id, "task_id": task_id, "stdout": stdout, "stderr": stderr}
                )

                if not success:
                    all_success = False

                # Update task status
                final_status = "completed" if success else "failed"
                sync_update_task_status(
                    task_id,
                    final_status,
                    completed_at=datetime.utcnow(),
                    stdout=stdout,
                    stderr=stderr,
                    exit_code=exit_code,
                    result_json={"stdout": stdout, "stderr": stderr, "exit_code": exit_code}
                )
                sync_publish_job_event(
                    JobEventChannels.TASK_COMPLETE,
                    {"job_id": job_id, "task_id": task_id, "status": final_status, "exit_code": exit_code}
                )

            except Exception as e:
                all_success = False
                sync_update_task_status(
                    task_id,
                    "failed",
                    completed_at=datetime.utcnow(),
                    error_message=str(e),
                    stderr=str(e)
                )
                sync_publish_job_event(
                    JobEventChannels.TASK_COMPLETE,
                    {"job_id": job_id, "task_id": task_id, "status": "failed", "exit_code": 1}
                )

        # Check if job was cancelled
        if sync_check_job_cancelled(job_id):
            final_job_status = "cancelled"
            all_success = False
        else:
            final_job_status = "completed" if all_success else "failed"

        # Update job status
        sync_update_job_status(job_id, final_job_status, completed_at=datetime.utcnow())
        sync_publish_job_event(
            JobEventChannels.JOB_COMPLETE,
            {"job_id": job_id, "status": final_job_status, "success": all_success}
        )

        return {"success": all_success, "job_id": job_id}

    except Exception as e:
        sync_update_job_status(
            job_id,
            "failed",
            completed_at=datetime.utcnow(),
            error_message=str(e)
        )
        sync_publish_job_event(
            JobEventChannels.JOB_COMPLETE,
            {"job_id": job_id, "status": "failed", "success": False}
        )
        return {"success": False, "error": str(e)}


@celery_app.task
def example_async_task(name: str) -> str:
    """示例异步任务"""
    return f"Hello, {name}! This is an async task."
