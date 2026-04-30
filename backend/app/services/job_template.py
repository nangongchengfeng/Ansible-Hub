from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_template import JobTemplate
from app.models.job_execution import JobExecution
from app.models.user import User
from app.schemas.job_template import (
    JobTemplateCreate,
    JobTemplateUpdate,
    JobTemplateExecute,
    SaveTemplateFromJob,
    TargetType,
)
from app.schemas.job_execution import JobExecutionCreate
from app.services.business_node import BusinessNodeService
from app.services.job_execution import JobExecutionService


class JobTemplateService:
    """作业模板服务"""

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        template_id: int,
    ) -> Optional[JobTemplate]:
        """通过 ID 获取作业模板"""
        result = await db.execute(
            select(JobTemplate)
            .where(JobTemplate.id == template_id)
            .options(
                selectinload(JobTemplate.creator),
                selectinload(JobTemplate.playbook),
                selectinload(JobTemplate.script),
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        job_type: Optional[str] = None,
        is_enabled: Optional[bool] = None,
        created_by: Optional[int] = None,
        business_node_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Tuple[int, List[JobTemplate]]:
        """获取作业模板列表"""
        # Build conditions
        conditions = []
        if job_type:
            conditions.append(JobTemplate.job_type == job_type)
        if is_enabled is not None:
            conditions.append(JobTemplate.is_enabled == is_enabled)
        if created_by is not None:
            conditions.append(JobTemplate.created_by == created_by)
        if business_node_id is not None:
            conditions.append(JobTemplate.business_node_id == business_node_id)
        if search:
            conditions.append(
                or_(
                    JobTemplate.name.contains(search),
                    JobTemplate.description.contains(search),
                )
            )

        # Count
        count_query = select(JobTemplate.id)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # Query data
        data_query = select(JobTemplate).options(
            selectinload(JobTemplate.creator),
        )
        if conditions:
            data_query = data_query.where(and_(*conditions))
        data_query = data_query.order_by(desc(JobTemplate.created_at)).offset(skip).limit(limit)
        data_result = await db.execute(data_query)
        templates = list(data_result.scalars().all())

        return total, templates

    @staticmethod
    async def create(
        db: AsyncSession,
        template_in: JobTemplateCreate,
        created_by: int,
    ) -> JobTemplate:
        """创建作业模板"""
        # Prepare template data
        template_data = {
            "name": template_in.name,
            "description": template_in.description,
            "job_type": template_in.job_type,
            "is_enabled": template_in.is_enabled,
            "created_by": created_by,
            "business_node_id": template_in.business_node_id,
        }

        # Set content based on job_type
        if template_in.job_type == "shell":
            template_data["shell_command"] = template_in.shell_command
        elif template_in.job_type == "module":
            template_data["module_name"] = template_in.module_name
            template_data["module_args"] = template_in.module_args
        elif template_in.job_type == "playbook":
            template_data["playbook_id"] = template_in.playbook_id
            template_data["playbook_version"] = template_in.playbook_version
        elif template_in.job_type == "script":
            template_data["script_id"] = template_in.script_id
            template_data["script_version"] = template_in.script_version

        # Set target info
        template_data["target_type"] = template_in.target_type.value
        if template_in.target_type == TargetType.HOST:
            template_data["target_host_ids"] = [template_in.target_host_id]
        elif template_in.target_type == TargetType.HOSTS:
            template_data["target_host_ids"] = template_in.target_host_ids
        elif template_in.target_type == TargetType.BUSINESS_NODE:
            template_data["target_business_node_id"] = template_in.target_business_node_id

        # Create template
        template = JobTemplate(**template_data)
        db.add(template)
        await db.commit()
        await db.refresh(template)

        # Load relationships
        result = await db.execute(
            select(JobTemplate)
            .where(JobTemplate.id == template.id)
            .options(
                selectinload(JobTemplate.creator),
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update(
        db: AsyncSession,
        template: JobTemplate,
        template_in: JobTemplateUpdate,
    ) -> JobTemplate:
        """更新作业模板"""
        # Update template metadata
        update_data = template_in.model_dump(exclude_unset=True)

        # Handle target_type conversion
        if "target_type" in update_data and update_data["target_type"] is not None:
            update_data["target_type"] = update_data["target_type"].value

        # Handle target_host_ids for single host
        if "target_host_id" in update_data and update_data["target_host_id"] is not None:
            update_data["target_host_ids"] = [update_data["target_host_id"]]
            del update_data["target_host_id"]

        # Apply updates
        for field, value in update_data.items():
            setattr(template, field, value)

        await db.commit()
        await db.refresh(template)

        # Load relationships
        result = await db.execute(
            select(JobTemplate)
            .where(JobTemplate.id == template.id)
            .options(
                selectinload(JobTemplate.creator),
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def delete(
        db: AsyncSession,
        template: JobTemplate,
    ) -> None:
        """删除作业模板"""
        await db.delete(template)
        await db.commit()

    @staticmethod
    async def execute(
        db: AsyncSession,
        template: JobTemplate,
        execute_in: Optional[JobTemplateExecute],
        created_by: int,
    ) -> Tuple[JobExecution, Dict[str, Any]]:
        """执行作业模板"""
        # Build job execution create data from template
        job_type = execute_in.job_type if (execute_in and execute_in.job_type) else template.job_type
        target_type = execute_in.target_type if (execute_in and execute_in.target_type) else TargetType(template.target_type)

        # Build JobExecutionCreate
        job_data = {
            "job_type": job_type,
            "target_type": target_type,
        }

        # Set content
        if job_type == "shell":
            job_data["shell_command"] = (
                execute_in.shell_command
                if (execute_in and execute_in.shell_command)
                else template.shell_command
            )
        elif job_type == "module":
            job_data["module_name"] = (
                execute_in.module_name
                if (execute_in and execute_in.module_name)
                else template.module_name
            )
            job_data["module_args"] = (
                execute_in.module_args
                if (execute_in and execute_in.module_args)
                else template.module_args
            )
        elif job_type == "playbook":
            job_data["playbook_id"] = (
                execute_in.playbook_id
                if (execute_in and execute_in.playbook_id)
                else template.playbook_id
            )
            job_data["playbook_version"] = (
                execute_in.playbook_version
                if (execute_in and execute_in.playbook_version)
                else template.playbook_version
            )
        elif job_type == "script":
            job_data["script_id"] = (
                execute_in.script_id
                if (execute_in and execute_in.script_id)
                else template.script_id
            )
            job_data["script_version"] = (
                execute_in.script_version
                if (execute_in and execute_in.script_version)
                else template.script_version
            )

        # Set target
        if target_type == TargetType.HOST:
            job_data["target_host_id"] = (
                execute_in.target_host_id
                if (execute_in and execute_in.target_host_id)
                else (template.target_host_ids[0] if template.target_host_ids else None)
            )
        elif target_type == TargetType.HOSTS:
            job_data["target_host_ids"] = (
                execute_in.target_host_ids
                if (execute_in and execute_in.target_host_ids)
                else template.target_host_ids
            )
        elif target_type == TargetType.BUSINESS_NODE:
            job_data["target_business_node_id"] = (
                execute_in.target_business_node_id
                if (execute_in and execute_in.target_business_node_id)
                else template.target_business_node_id
            )

        # Create and submit job
        job_create = JobExecutionCreate(**job_data)
        return await JobExecutionService.create(db, job_create, created_by)

    @staticmethod
    async def save_from_job(
        db: AsyncSession,
        job: JobExecution,
        save_in: SaveTemplateFromJob,
        created_by: int,
    ) -> JobTemplate:
        """从历史作业保存为模板"""
        # Build template create data from job
        template_data = {
            "name": save_in.name,
            "description": save_in.description,
            "job_type": job.job_type,
            "is_enabled": True,
            "created_by": created_by,
            "business_node_id": save_in.business_node_id,
        }

        # Set content from job
        if job.job_type == "shell":
            template_data["shell_command"] = job.shell_command
        elif job.job_type == "module":
            template_data["module_name"] = job.module_name
            template_data["module_args"] = job.module_args
        elif job.job_type == "playbook":
            template_data["playbook_id"] = job.playbook_id
            template_data["playbook_version"] = job.playbook_version
        elif job.job_type == "script":
            template_data["script_id"] = job.script_id
            template_data["script_version"] = job.script_version

        # Set target info from job
        template_data["target_type"] = job.target_type
        template_data["target_host_ids"] = job.target_host_ids
        template_data["target_business_node_id"] = job.target_business_node_id

        # Create template
        template = JobTemplate(**template_data)
        db.add(template)
        await db.commit()
        await db.refresh(template)

        # Load relationships
        result = await db.execute(
            select(JobTemplate)
            .where(JobTemplate.id == template.id)
            .options(
                selectinload(JobTemplate.creator),
            )
        )
        return result.scalar_one_or_none()
