from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_superuser
from app.models.user import User
from app.models.script import Script, ScriptVersion
from app.schemas.script import (
    ScriptCreate,
    ScriptUpdate,
    ScriptResponse,
    ScriptDetailResponse,
    ScriptVersionSimple,
    ScriptVersionDetail,
    ScriptVersionListResponse,
    ScriptRollback,
    ScriptRollbackResponse,
)
from app.services.script import ScriptService

router = APIRouter(prefix="/scripts", tags=["脚本管理"])


@router.get("", response_model=List[ScriptResponse])
async def get_scripts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取脚本列表"""
    total, scripts = await ScriptService.get_list(
        db=db, skip=skip, limit=limit, search=search, language=language
    )
    return scripts


@router.post("", response_model=ScriptResponse, status_code=status.HTTP_201_CREATED)
async def create_script(
    script_in: ScriptCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建脚本"""
    script = await ScriptService.create(
        db=db, script_in=script_in, created_by=current_user.id
    )
    return script


@router.get("/{script_id}", response_model=ScriptDetailResponse)
async def get_script(
    script_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取脚本详情"""
    script = await ScriptService.get_by_id(db, script_id)
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="脚本不存在"
        )
    return script


@router.put("/{script_id}", response_model=ScriptResponse)
async def update_script(
    script_id: int,
    script_in: ScriptUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新脚本（创建新版本）"""
    script = await ScriptService.get_by_id(db, script_id)
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="脚本不存在"
        )

    script = await ScriptService.update(db, script, script_in, current_user.id)
    return script


@router.delete("/{script_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_script(
    script_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除脚本"""
    script = await ScriptService.get_by_id(db, script_id)
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="脚本不存在"
        )
    await ScriptService.delete(db, script)
    return None


@router.get("/{script_id}/versions", response_model=ScriptVersionListResponse)
async def get_script_versions(
    script_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取脚本版本列表"""
    # Check if script exists
    script = await ScriptService.get_by_id(db, script_id)
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="脚本不存在"
        )

    total, versions = await ScriptService.get_versions(
        db=db, script_id=script_id, skip=skip, limit=limit
    )
    return {"items": versions, "total": total}


@router.get("/{script_id}/versions/{version}", response_model=ScriptVersionDetail)
async def get_script_version(
    script_id: int,
    version: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取脚本指定版本"""
    script_version = await ScriptService.get_version_by_number(db, script_id, version)
    if not script_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在"
        )
    return script_version


@router.get("/{script_id}/versions/{version1}/diff/{version2}")
async def compare_script_versions(
    script_id: int,
    version1: int,
    version2: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """比较两个版本"""
    v1, v2, diff = await ScriptService.compare_versions(db, script_id, version1, version2)
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


@router.post("/{script_id}/rollback", response_model=ScriptRollbackResponse)
async def rollback_script(
    script_id: int,
    rollback_in: ScriptRollback,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """回滚到指定版本（创建新版本）"""
    script = await ScriptService.get_by_id(db, script_id)
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="脚本不存在"
        )

    try:
        script, rolled_back_from, rolled_back_to = await ScriptService.rollback(
            db=db, script=script, target_version=rollback_in.target_version, created_by=current_user.id
        )
        return {
            "id": script.id,
            "latest_version": script.latest_version.version if script.latest_version else 0,
            "rolled_back_from": rolled_back_from,
            "rolled_back_to": rolled_back_to
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
