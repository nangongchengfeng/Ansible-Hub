from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_superuser
from app.models.user import User
from app.models.playbook import Playbook, PlaybookVersion
from app.schemas.playbook import (
    PlaybookCreate,
    PlaybookUpdate,
    PlaybookResponse,
    PlaybookDetailResponse,
    PlaybookVersionSimple,
    PlaybookVersionDetail,
    PlaybookVersionListResponse,
    PlaybookRollback,
    PlaybookRollbackResponse,
)
from app.services.playbook import PlaybookService

router = APIRouter(prefix="/playbooks", tags=["剧本管理"])


@router.get("", response_model=List[PlaybookResponse])
async def get_playbooks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取剧本列表"""
    total, playbooks = await PlaybookService.get_list(
        db=db, skip=skip, limit=limit, search=search
    )
    return playbooks


@router.post("", response_model=PlaybookResponse, status_code=status.HTTP_201_CREATED)
async def create_playbook(
    playbook_in: PlaybookCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建剧本"""
    playbook = await PlaybookService.create(
        db=db, playbook_in=playbook_in, created_by=current_user.id
    )
    return playbook


@router.get("/{playbook_id}", response_model=PlaybookDetailResponse)
async def get_playbook(
    playbook_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取剧本详情"""
    playbook = await PlaybookService.get_by_id(db, playbook_id)
    if not playbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="剧本不存在"
        )
    return playbook


@router.put("/{playbook_id}", response_model=PlaybookResponse)
async def update_playbook(
    playbook_id: int,
    playbook_in: PlaybookUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新剧本（创建新版本）"""
    playbook = await PlaybookService.get_by_id(db, playbook_id)
    if not playbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="剧本不存在"
        )

    playbook = await PlaybookService.update(db, playbook, playbook_in, current_user.id)
    return playbook


@router.delete("/{playbook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playbook(
    playbook_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除剧本"""
    playbook = await PlaybookService.get_by_id(db, playbook_id)
    if not playbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="剧本不存在"
        )
    await PlaybookService.delete(db, playbook)
    return None


@router.get("/{playbook_id}/versions", response_model=PlaybookVersionListResponse)
async def get_playbook_versions(
    playbook_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取剧本版本列表"""
    # Check if playbook exists
    playbook = await PlaybookService.get_by_id(db, playbook_id)
    if not playbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="剧本不存在"
        )

    total, versions = await PlaybookService.get_versions(
        db=db, playbook_id=playbook_id, skip=skip, limit=limit
    )
    return {"items": versions, "total": total}


@router.get("/{playbook_id}/versions/{version}", response_model=PlaybookVersionDetail)
async def get_playbook_version(
    playbook_id: int,
    version: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取剧本指定版本"""
    playbook_version = await PlaybookService.get_version_by_number(db, playbook_id, version)
    if not playbook_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在"
        )
    return playbook_version


@router.get("/{playbook_id}/versions/{version1}/diff/{version2}")
async def compare_playbook_versions(
    playbook_id: int,
    version1: int,
    version2: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """比较两个版本"""
    v1, v2, diff = await PlaybookService.compare_versions(db, playbook_id, version1, version2)
    if not v1 or not v2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="一个或多个版本不存在"
        )

    return {
        "version1": version1,
        "version2": version2,
        "diff": diff
    }


@router.post("/{playbook_id}/rollback", response_model=PlaybookRollbackResponse)
async def rollback_playbook(
    playbook_id: int,
    rollback_in: PlaybookRollback,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """回滚到指定版本（创建新版本）"""
    playbook = await PlaybookService.get_by_id(db, playbook_id)
    if not playbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="剧本不存在"
        )

    try:
        playbook, rolled_back_from, rolled_back_to = await PlaybookService.rollback(
            db=db, playbook=playbook, target_version=rollback_in.target_version, created_by=current_user.id
        )
        return {
            "id": playbook.id,
            "latest_version": playbook.latest_version.version if playbook.latest_version else 0,
            "rolled_back_from": rolled_back_from,
            "rolled_back_to": rolled_back_to
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
