from typing import Optional, List, Tuple
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload, aliased
from sqlalchemy.ext.asyncio import AsyncSession
from difflib import unified_diff
from app.models.script import Script, ScriptVersion
from app.models.user import User
from app.schemas.script import ScriptCreate, ScriptUpdate


class ScriptService:
    """脚本服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, script_id: int) -> Optional[Script]:
        """通过ID获取脚本"""
        result = await db.execute(
            select(Script)
            .where(Script.id == script_id)
            .options(
                selectinload(Script.creator),
                selectinload(Script.versions).selectinload(ScriptVersion.creator)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        language: Optional[str] = None,
    ) -> Tuple[int, List[Script]]:
        """获取脚本列表"""
        # Build conditions
        conditions = []
        if search:
            conditions.append(
                or_(
                    Script.name.contains(search),
                    Script.description.contains(search)
                )
            )
        if language:
            conditions.append(Script.language == language)

        # Count
        count_query = select(Script.id)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # Query data with latest version
        data_query = select(Script).options(
            selectinload(Script.creator),
            selectinload(Script.versions).selectinload(ScriptVersion.creator)
        )
        if conditions:
            data_query = data_query.where(and_(*conditions))
        data_query = data_query.order_by(Script.created_at.desc()).offset(skip).limit(limit)
        data_result = await db.execute(data_query)
        scripts = list(data_result.scalars().all())

        return total, scripts

    @staticmethod
    async def create(
        db: AsyncSession,
        script_in: ScriptCreate,
        created_by: int,
    ) -> Script:
        """创建脚本（同时创建v1版本）"""
        # Create script
        script = Script(
            name=script_in.name,
            description=script_in.description,
            language=script_in.language,
            created_by=created_by,
        )
        db.add(script)
        await db.flush()  # Flush to get script ID

        # Create v1 version
        script_version = ScriptVersion(
            script_id=script.id,
            version=1,
            content=script_in.content,
            change_description=script_in.change_description or "Initial version",
            created_by=created_by,
        )
        db.add(script_version)

        await db.commit()
        await db.refresh(script)

        # Load relationships
        result = await db.execute(
            select(Script)
            .where(Script.id == script.id)
            .options(
                selectinload(Script.creator),
                selectinload(Script.versions).selectinload(ScriptVersion.creator)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update(
        db: AsyncSession,
        script: Script,
        script_in: ScriptUpdate,
        updated_by: int,
    ) -> Script:
        """更新脚本（创建新版本）"""
        # Update script metadata
        update_data = script_in.model_dump(exclude_unset=True, exclude={"content", "change_description"})
        for field, value in update_data.items():
            setattr(script, field, value)

        # Get current max version
        max_version_result = await db.execute(
            select(func.max(ScriptVersion.version))
            .where(ScriptVersion.script_id == script.id)
        )
        current_version = max_version_result.scalar_one_or_none() or 0
        new_version = current_version + 1

        # Create new version
        script_version = ScriptVersion(
            script_id=script.id,
            version=new_version,
            content=script_in.content,
            change_description=script_in.change_description,
            created_by=updated_by,
        )
        db.add(script_version)

        await db.commit()
        await db.refresh(script)

        # Load relationships
        result = await db.execute(
            select(Script)
            .where(Script.id == script.id)
            .options(
                selectinload(Script.creator),
                selectinload(Script.versions).selectinload(ScriptVersion.creator)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def delete(db: AsyncSession, script: Script):
        """删除脚本（级联删除所有版本）"""
        await db.delete(script)
        await db.commit()

    @staticmethod
    async def get_versions(
        db: AsyncSession,
        script_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[int, List[ScriptVersion]]:
        """获取脚本版本列表"""
        # Count
        count_query = select(ScriptVersion.id).where(ScriptVersion.script_id == script_id)
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # Query data
        data_query = select(ScriptVersion).options(
            selectinload(ScriptVersion.creator)
        ).where(ScriptVersion.script_id == script_id)
        data_query = data_query.order_by(ScriptVersion.version.desc()).offset(skip).limit(limit)
        data_result = await db.execute(data_query)
        versions = list(data_result.scalars().all())

        return total, versions

    @staticmethod
    async def get_version_by_number(
        db: AsyncSession,
        script_id: int,
        version: int,
    ) -> Optional[ScriptVersion]:
        """获取脚本指定版本"""
        result = await db.execute(
            select(ScriptVersion)
            .where(
                ScriptVersion.script_id == script_id,
                ScriptVersion.version == version
            )
            .options(
                selectinload(ScriptVersion.creator)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def compare_versions(
        db: AsyncSession,
        script_id: int,
        version1: int,
        version2: int,
    ) -> Tuple[Optional[ScriptVersion], Optional[ScriptVersion], str]:
        """比较两个版本"""
        v1_alias = aliased(ScriptVersion)
        v2_alias = aliased(ScriptVersion)

        result = await db.execute(
            select(v1_alias, v2_alias)
            .where(
                v1_alias.script_id == script_id,
                v1_alias.version == version1,
                v2_alias.script_id == script_id,
                v2_alias.version == version2,
            )
        )
        row = result.one_or_none()

        if not row:
            return None, None, ""

        v1, v2 = row

        # Generate diff
        v1_lines = v1.content.splitlines(keepends=True)
        v2_lines = v2.content.splitlines(keepends=True)

        diff_text = "".join(unified_diff(
            v1_lines,
            v2_lines,
            fromfile=f"Version {version1}",
            tofile=f"Version {version2}",
        ))

        return v1, v2, diff_text

    @staticmethod
    async def rollback(
        db: AsyncSession,
        script: Script,
        target_version: int,
        created_by: int,
    ) -> Tuple[Script, int, int]:
        """回滚到指定版本（创建新版本）"""
        # Get target version
        target_version_obj = await db.execute(
            select(ScriptVersion).where(
                ScriptVersion.script_id == script.id,
                ScriptVersion.version == target_version
            )
        )
        target_version_data = target_version_obj.scalar_one_or_none()
        if not target_version_data:
            raise ValueError(f"Version {target_version} not found")

        # Get current max version
        max_version_result = await db.execute(
            select(func.max(ScriptVersion.version))
            .where(ScriptVersion.script_id == script.id)
        )
        current_version = max_version_result.scalar_one_or_none() or 0
        new_version = current_version + 1

        # Create new version
        script_version = ScriptVersion(
            script_id=script.id,
            version=new_version,
            content=target_version_data.content,
            change_description=f"Rollback to version {target_version}",
            created_by=created_by,
        )
        db.add(script_version)

        await db.commit()
        await db.refresh(script)

        # Load relationships
        result = await db.execute(
            select(Script)
            .where(Script.id == script.id)
            .options(
                selectinload(Script.creator),
                selectinload(Script.versions).selectinload(ScriptVersion.creator)
            )
        )
        return result.scalar_one_or_none(), current_version, target_version
