from typing import Optional, List, Tuple
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload, aliased
from sqlalchemy.ext.asyncio import AsyncSession
from difflib import unified_diff
from app.models.playbook import Playbook, PlaybookVersion
from app.models.user import User
from app.schemas.playbook import PlaybookCreate, PlaybookUpdate


class PlaybookService:
    """剧本服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, playbook_id: int) -> Optional[Playbook]:
        """通过ID获取剧本"""
        result = await db.execute(
            select(Playbook)
            .where(Playbook.id == playbook_id)
            .options(
                selectinload(Playbook.creator),
                selectinload(Playbook.versions).selectinload(PlaybookVersion.creator)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> Tuple[int, List[Playbook]]:
        """获取剧本列表"""
        # Build conditions
        conditions = []
        if search:
            conditions.append(
                or_(
                    Playbook.name.contains(search),
                    Playbook.description.contains(search)
                )
            )

        # Count
        count_query = select(Playbook.id)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # Query data with latest version
        data_query = select(Playbook).options(
            selectinload(Playbook.creator),
            selectinload(Playbook.versions).selectinload(PlaybookVersion.creator)
        )
        if conditions:
            data_query = data_query.where(and_(*conditions))
        data_query = data_query.order_by(Playbook.created_at.desc()).offset(skip).limit(limit)
        data_result = await db.execute(data_query)
        playbooks = list(data_result.scalars().all())

        return total, playbooks

    @staticmethod
    async def create(
        db: AsyncSession,
        playbook_in: PlaybookCreate,
        created_by: int,
    ) -> Playbook:
        """创建剧本（同时创建v1版本）"""
        # Create playbook
        playbook = Playbook(
            name=playbook_in.name,
            description=playbook_in.description,
            created_by=created_by,
        )
        db.add(playbook)
        await db.flush()  # Flush to get playbook ID

        # Create v1 version
        playbook_version = PlaybookVersion(
            playbook_id=playbook.id,
            version=1,
            content=playbook_in.content,
            change_description=playbook_in.change_description or "Initial version",
            created_by=created_by,
        )
        db.add(playbook_version)

        await db.commit()
        await db.refresh(playbook)

        # Load relationships
        result = await db.execute(
            select(Playbook)
            .where(Playbook.id == playbook.id)
            .options(
                selectinload(Playbook.creator),
                selectinload(Playbook.versions).selectinload(PlaybookVersion.creator)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update(
        db: AsyncSession,
        playbook: Playbook,
        playbook_in: PlaybookUpdate,
        updated_by: int,
    ) -> Playbook:
        """更新剧本（创建新版本）"""
        # Update playbook metadata
        update_data = playbook_in.model_dump(exclude_unset=True, exclude={"content", "change_description"})
        for field, value in update_data.items():
            setattr(playbook, field, value)

        # Get current max version
        max_version_result = await db.execute(
            select(func.max(PlaybookVersion.version))
            .where(PlaybookVersion.playbook_id == playbook.id)
        )
        current_version = max_version_result.scalar_one_or_none() or 0
        new_version = current_version + 1

        # Create new version
        playbook_version = PlaybookVersion(
            playbook_id=playbook.id,
            version=new_version,
            content=playbook_in.content,
            change_description=playbook_in.change_description,
            created_by=updated_by,
        )
        db.add(playbook_version)

        await db.commit()
        await db.refresh(playbook)

        # Load relationships
        result = await db.execute(
            select(Playbook)
            .where(Playbook.id == playbook.id)
            .options(
                selectinload(Playbook.creator),
                selectinload(Playbook.versions).selectinload(PlaybookVersion.creator)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def delete(db: AsyncSession, playbook: Playbook):
        """删除剧本（级联删除所有版本）"""
        await db.delete(playbook)
        await db.commit()

    @staticmethod
    async def get_versions(
        db: AsyncSession,
        playbook_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[int, List[PlaybookVersion]]:
        """获取剧本版本列表"""
        # Count
        count_query = select(PlaybookVersion.id).where(PlaybookVersion.playbook_id == playbook_id)
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # Query data
        data_query = select(PlaybookVersion).options(
            selectinload(PlaybookVersion.creator)
        ).where(PlaybookVersion.playbook_id == playbook_id)
        data_query = data_query.order_by(PlaybookVersion.version.desc()).offset(skip).limit(limit)
        data_result = await db.execute(data_query)
        versions = list(data_result.scalars().all())

        return total, versions

    @staticmethod
    async def get_version_by_number(
        db: AsyncSession,
        playbook_id: int,
        version: int,
    ) -> Optional[PlaybookVersion]:
        """获取剧本指定版本"""
        result = await db.execute(
            select(PlaybookVersion)
            .where(
                PlaybookVersion.playbook_id == playbook_id,
                PlaybookVersion.version == version
            )
            .options(
                selectinload(PlaybookVersion.creator)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def compare_versions(
        db: AsyncSession,
        playbook_id: int,
        version1: int,
        version2: int,
    ) -> Tuple[Optional[PlaybookVersion], Optional[PlaybookVersion], str]:
        """比较两个版本"""
        v1_alias = aliased(PlaybookVersion)
        v2_alias = aliased(PlaybookVersion)

        result = await db.execute(
            select(v1_alias, v2_alias)
            .where(
                v1_alias.playbook_id == playbook_id,
                v1_alias.version == version1,
                v2_alias.playbook_id == playbook_id,
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
        playbook: Playbook,
        target_version: int,
        created_by: int,
    ) -> Tuple[Playbook, int, int]:
        """回滚到指定版本（创建新版本）"""
        # Get target version
        target_version_obj = await db.execute(
            select(PlaybookVersion).where(
                PlaybookVersion.playbook_id == playbook.id,
                PlaybookVersion.version == target_version
            )
        )
        target_version_data = target_version_obj.scalar_one_or_none()
        if not target_version_data:
            raise ValueError(f"Version {target_version} not found")

        # Get current max version
        max_version_result = await db.execute(
            select(func.max(PlaybookVersion.version))
            .where(PlaybookVersion.playbook_id == playbook.id)
        )
        current_version = max_version_result.scalar_one_or_none() or 0
        new_version = current_version + 1

        # Create new version
        playbook_version = PlaybookVersion(
            playbook_id=playbook.id,
            version=new_version,
            content=target_version_data.content,
            change_description=f"Rollback to version {target_version}",
            created_by=created_by,
        )
        db.add(playbook_version)

        await db.commit()
        await db.refresh(playbook)

        # Load relationships
        result = await db.execute(
            select(Playbook)
            .where(Playbook.id == playbook.id)
            .options(
                selectinload(Playbook.creator),
                selectinload(Playbook.versions).selectinload(PlaybookVersion.creator)
            )
        )
        return result.scalar_one_or_none(), current_version, target_version
