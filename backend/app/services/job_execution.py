from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.job_execution import JobExecution, Task
from app.models.user import User
from app.models.host import Host
from app.schemas.job_execution import JobExecutionCreate, TargetType
from app.services.host import HostService
from app.services.command_filter_rule import CommandFilterRuleService
from app.services.script import ScriptService
from app.services.playbook import PlaybookService
from app.tasks import execute_job


class JobExecutionService:
    """作业执行服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, job_id: int) -> Optional[JobExecution]:
        """通过ID获取作业"""
        result = await db.execute(
            select(JobExecution)
            .where(JobExecution.id == job_id)
            .options(
                selectinload(JobExecution.creator),
                selectinload(JobExecution.tasks).selectinload(Task.host),
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        job_type: Optional[str] = None,
        status: Optional[str] = None,
        created_by: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        search: Optional[str] = None,
    ) -> Tuple[int, List[JobExecution]]:
        """获取作业列表"""
        # Build conditions
        conditions = []
        if job_type:
            conditions.append(JobExecution.job_type == job_type)
        if status:
            conditions.append(JobExecution.status == status)
        if created_by is not None:
            conditions.append(JobExecution.created_by == created_by)
        if start_time:
            conditions.append(JobExecution.created_at >= start_time)
        if end_time:
            conditions.append(JobExecution.created_at <= end_time)
        if search:
            conditions.append(
                or_(
                    JobExecution.shell_command.contains(search),
                    JobExecution.module_name.contains(search),
                )
            )

        # Count
        count_query = select(JobExecution.id)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # Query data
        data_query = select(JobExecution).options(
            selectinload(JobExecution.creator),
        )
        if conditions:
            data_query = data_query.where(and_(*conditions))
        data_query = data_query.order_by(desc(JobExecution.created_at)).offset(skip).limit(limit)
        data_result = await db.execute(data_query)
        jobs = list(data_result.scalars().all())

        return total, jobs

    @staticmethod
    async def get_tasks_by_job_id(
        db: AsyncSession,
        job_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[int, List[Task]]:
        """获取作业的任务列表"""
        # Count
        count_query = select(Task.id).where(Task.job_execution_id == job_id)
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # Query data
        data_query = select(Task).options(
            selectinload(Task.host),
        ).where(Task.job_execution_id == job_id)
        data_query = data_query.order_by(Task.id).offset(skip).limit(limit)
        data_result = await db.execute(data_query)
        tasks = list(data_result.scalars().all())

        return total, tasks

    @staticmethod
    async def get_task_by_id(db: AsyncSession, task_id: int) -> Optional[Task]:
        """通过ID获取任务"""
        result = await db.execute(
            select(Task)
            .where(Task.id == task_id)
            .options(
                selectinload(Task.host),
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def _resolve_target_hosts(
        db: AsyncSession,
        job_in: JobExecutionCreate,
    ) -> List[Host]:
        """解析目标主机列表"""
        hosts: List[Host] = []

        if job_in.target_type == TargetType.HOST:
            host = await HostService.get_by_id(db, job_in.target_host_id)
            if not host:
                raise ValueError(f"Host {job_in.target_host_id} not found")
            if not host.is_enabled:
                raise ValueError(f"Host {host.name} is disabled")
            hosts = [host]

        elif job_in.target_type == TargetType.HOSTS:
            for host_id in job_in.target_host_ids:
                host = await HostService.get_by_id(db, host_id)
                if not host:
                    raise ValueError(f"Host {host_id} not found")
                if not host.is_enabled:
                    raise ValueError(f"Host {host.name} is disabled")
                hosts.append(host)

        elif job_in.target_type == TargetType.BUSINESS_NODE:
            _, hosts = await HostService.get_by_business_node(
                db, job_in.target_business_node_id, include_children=True, only_enabled=True
            )
            if not hosts:
                raise ValueError("No enabled hosts found in the specified business node")

        return hosts

    @staticmethod
    async def _check_command(
        db: AsyncSession,
        job_in: JobExecutionCreate,
    ) -> Tuple[bool, Dict[str, Any]]:
        """检查命令是否符合过滤规则"""
        command_to_check = ""

        if job_in.job_type == "shell":
            command_to_check = job_in.shell_command or ""
        elif job_in.job_type == "module":
            command_to_check = f"{job_in.module_name} {job_in.module_args or ''}"
        elif job_in.job_type == "script":
            # For scripts, we check the script content (or just allow if no command)
            script = await ScriptService.get_by_id(db, job_in.script_id)
            if not script:
                raise ValueError(f"Script {job_in.script_id} not found")
            # We don't check the content, just allow
            return True, {"allowed": True, "matched_rules": [], "severity": "allow", "message": "Script execution allowed"}
        elif job_in.job_type == "playbook":
            # For playbooks, we just allow
            playbook = await PlaybookService.get_by_id(db, job_in.playbook_id)
            if not playbook:
                raise ValueError(f"Playbook {job_in.playbook_id} not found")
            return True, {"allowed": True, "matched_rules": [], "severity": "allow", "message": "Playbook execution allowed"}

        if command_to_check:
            allowed, matched_rules, severity = await CommandFilterRuleService.check_command(db, command_to_check)
            message = "Command allowed" if allowed else "Command blocked by filter rules"
            return allowed, {
                "allowed": allowed,
                "matched_rules": [{"id": r.id, "name": r.name, "action": r.action, "match_type": r.match_type, "pattern": r.pattern} for r in matched_rules],
                "severity": severity,
                "message": message
            }

        return True, {"allowed": True, "matched_rules": [], "severity": "allow", "message": "No command to check"}

    @staticmethod
    async def create(
        db: AsyncSession,
        job_in: JobExecutionCreate,
        created_by: int,
    ) -> Tuple[JobExecution, Dict[str, Any]]:
        """提交作业执行"""
        # Resolve target hosts
        hosts = await JobExecutionService._resolve_target_hosts(db, job_in)

        # Check command against filter rules
        command_check_passed, command_check_result = await JobExecutionService._check_command(db, job_in)

        # Prepare job data
        job_data = {
            "job_type": job_in.job_type,
            "status": "pending",
            "command_check_passed": command_check_passed,
            "command_check_result": command_check_result,
            "created_by": created_by,
        }

        # Set content based on job type
        if job_in.job_type == "shell":
            job_data["shell_command"] = job_in.shell_command
        elif job_in.job_type == "module":
            job_data["module_name"] = job_in.module_name
            job_data["module_args"] = job_in.module_args
        elif job_in.job_type == "playbook":
            job_data["playbook_id"] = job_in.playbook_id
            job_data["playbook_version"] = job_in.playbook_version
        elif job_in.job_type == "script":
            job_data["script_id"] = job_in.script_id
            job_data["script_version"] = job_in.script_version

        # Set target info
        job_data["target_type"] = job_in.target_type.value
        if job_in.target_type == TargetType.HOST:
            job_data["target_host_ids"] = [job_in.target_host_id]
        elif job_in.target_type == TargetType.HOSTS:
            job_data["target_host_ids"] = job_in.target_host_ids
        elif job_in.target_type == TargetType.BUSINESS_NODE:
            job_data["target_business_node_id"] = job_in.target_business_node_id
            job_data["target_host_ids"] = [h.id for h in hosts]

        # Create job
        job = JobExecution(**job_data)
        db.add(job)
        await db.flush()

        # Create tasks for each host
        for host in hosts:
            # Resolve connection config for this host
            connection_config = await HostService.resolve_connection_config(db, host)
            task = Task(
                job_execution_id=job.id,
                host_id=host.id,
                status="pending",
                connection_config=connection_config.model_dump() if connection_config else None,
            )
            db.add(task)

        await db.commit()
        await db.refresh(job)

        # If command check passed, queue the job
        if command_check_passed:
            execute_job.delay(job.id)

        # Load relationships
        result = await db.execute(
            select(JobExecution)
            .where(JobExecution.id == job.id)
            .options(
                selectinload(JobExecution.creator),
                selectinload(JobExecution.tasks).selectinload(Task.host),
            )
        )
        return result.scalar_one_or_none(), command_check_result

    @staticmethod
    async def cancel_job(
        db: AsyncSession,
        job_id: int,
        current_user: User,
    ) -> JobExecution:
        """取消作业"""
        job = await JobExecutionService.get_by_id(db, job_id)
        if not job:
            raise ValueError("Job not found")

        # Check permissions
        if current_user.role != "super_admin" and job.created_by != current_user.id:
            raise ValueError("You don't have permission to cancel this job")

        # Check if job is already in terminal state
        if job.status in ["completed", "failed", "cancelled"]:
            raise ValueError("Job is already completed or cancelled")

        # Update job status
        job.status = "cancelled"
        job.completed_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()

        # Update all running/pending tasks to cancelled/skipped
        for task in job.tasks:
            if task.status in ["pending", "running"]:
                task.status = "skipped"
                task.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(job)

        # Publish cancellation event
        from app.core.job_events import publish_job_event, JobEventChannels
        await publish_job_event(
            JobEventChannels.JOB_STATUS,
            {"job_id": job.id, "status": "cancelled"}
        )

        return job

    @staticmethod
    async def get_job_logs(
        db: AsyncSession,
        job_id: int,
    ) -> Dict[str, Any]:
        """获取作业完整日志"""
        job = await JobExecutionService.get_by_id(db, job_id)
        if not job:
            raise ValueError("Job not found")

        # Aggregate logs from all tasks
        logs = {
            "job_id": job.id,
            "job_type": job.job_type,
            "status": job.status,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "tasks": []
        }

        for task in job.tasks:
            task_log = {
                "task_id": task.id,
                "host_id": task.host_id,
                "host_name": task.host.name if task.host else None,
                "status": task.status,
                "stdout": task.stdout,
                "stderr": task.stderr,
                "exit_code": task.exit_code,
                "error_message": task.error_message,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            }
            logs["tasks"].append(task_log)

        return logs

    @staticmethod
    async def retry_job(
        db: AsyncSession,
        job_id: int,
        current_user: User,
    ) -> JobExecution:
        """重做作业（创建新作业）"""
        original_job = await JobExecutionService.get_by_id(db, job_id)
        if not original_job:
            raise ValueError("Original job not found")

        # Prepare data for new job
        job_data = {
            "job_type": original_job.job_type,
            "status": "pending",
            "command_check_passed": True,
            "created_by": current_user.id,
        }

        # Copy content based on job type
        if original_job.job_type == "shell":
            job_data["shell_command"] = original_job.shell_command
        elif original_job.job_type == "module":
            job_data["module_name"] = original_job.module_name
            job_data["module_args"] = original_job.module_args
        elif original_job.job_type == "playbook":
            job_data["playbook_id"] = original_job.playbook_id
            job_data["playbook_version"] = original_job.playbook_version
        elif original_job.job_type == "script":
            job_data["script_id"] = original_job.script_id
            job_data["script_version"] = original_job.script_version

        # Copy target info
        job_data["target_type"] = original_job.target_type
        job_data["target_host_ids"] = original_job.target_host_ids
        job_data["target_business_node_id"] = original_job.target_business_node_id

        # Create new job
        new_job = JobExecution(**job_data)
        db.add(new_job)
        await db.flush()

        # Create tasks for each host
        for host_id in original_job.target_host_ids or []:
            host = await HostService.get_by_id(db, host_id)
            if host and host.is_enabled:
                # Resolve connection config for this host
                connection_config = await HostService.resolve_connection_config(db, host)
                task = Task(
                    job_execution_id=new_job.id,
                    host_id=host.id,
                    status="pending",
                    connection_config=connection_config.model_dump() if connection_config else None,
                )
                db.add(task)

        await db.commit()
        await db.refresh(new_job)

        # Queue the job
        execute_job.delay(new_job.id)

        # Load relationships
        result = await db.execute(
            select(JobExecution)
            .where(JobExecution.id == new_job.id)
            .options(
                selectinload(JobExecution.creator),
            )
        )
        return result.scalar_one_or_none()
