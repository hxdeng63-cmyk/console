from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import CleanupPolicy
from app.services.cleanup_service import get_or_create_policy

router = APIRouter(prefix="/cleanup-policy", tags=["清理策略配置"])


class CleanupPolicyUpdate(BaseModel):
    alert_enabled: bool = True
    alert_days: int = Field(default=90, ge=1, le=3650)
    video_enabled: bool = True
    video_days: int = Field(default=60, ge=1, le=3650)
    strategy: Literal["scheduled", "immediate"] = "scheduled"
    execute_time: str = Field(default="02:00", pattern=r"^\d{2}:\d{2}$")


@router.get("")
async def get_cleanup_policy(db: AsyncSession = Depends(get_db)):
    """获取当前清理策略配置"""
    policy = await get_or_create_policy(db)
    return {
        "id": policy.id,
        "alert_enabled": policy.alert_enabled,
        "alert_days": policy.alert_days,
        "video_enabled": policy.video_enabled,
        "video_days": policy.video_days,
        "strategy": policy.strategy,
        "execute_time": policy.execute_time,
    }


@router.put("")
async def update_cleanup_policy(
    data: CleanupPolicyUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新清理策略配置"""
    policy = await get_or_create_policy(db)

    for field in CleanupPolicyUpdate.model_fields:
        setattr(policy, field, getattr(data, field))

    await db.commit()
    await db.refresh(policy)

    return {
        "id": policy.id,
        "alert_enabled": policy.alert_enabled,
        "alert_days": policy.alert_days,
        "video_enabled": policy.video_enabled,
        "video_days": policy.video_days,
        "strategy": policy.strategy,
        "execute_time": policy.execute_time,
    }
