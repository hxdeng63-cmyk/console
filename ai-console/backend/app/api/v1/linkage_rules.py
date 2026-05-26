from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.linkage_rule import LinkageRule
from app.models.deployment_schedule import DeploymentSchedule
from app.schemas.request.linkage_rule import (
    LinkageRuleRequest,
    LinkageRuleResponse,
    DeploymentScheduleRequest,
    DeploymentScheduleResponse,
)

router = APIRouter(prefix="/linkage-rules", tags=["linkage-rules"])


@router.get("", response_model=dict)
async def list_linkage_rules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    status: str = Query(None),
    trigger_mode: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(LinkageRule).where(LinkageRule.deleted_at.is_(None))

    if keyword:
        query = query.where(LinkageRule.rule_name.ilike(f"%{keyword}%"))
    if status:
        query = query.where(LinkageRule.status == status)
    if trigger_mode:
        query = query.where(LinkageRule.trigger_mode == trigger_mode)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": [LinkageRuleResponse.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/tree", response_model=list)
async def get_linkage_rule_tree(db: AsyncSession = Depends(get_db)):
    query = select(LinkageRule).where(LinkageRule.deleted_at.is_(None)).order_by(LinkageRule.importance_level)
    result = await db.execute(query)
    items = result.scalars().all()
    return [LinkageRuleResponse.model_validate(item) for item in items]


@router.get("/{item_id}", response_model=LinkageRuleResponse)
async def get_linkage_rule(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(LinkageRule).where(LinkageRule.id == item_id, LinkageRule.deleted_at.is_(None))
    result = await db.execute(query)
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Linkage rule not found")
    return LinkageRuleResponse.model_validate(rule)


@router.post("", response_model=LinkageRuleResponse)
async def create_linkage_rule(data: LinkageRuleRequest, db: AsyncSession = Depends(get_db)):
    rule = LinkageRule(**data.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return LinkageRuleResponse.model_validate(rule)


@router.put("/{item_id}", response_model=LinkageRuleResponse)
async def update_linkage_rule(item_id: int, data: LinkageRuleRequest, db: AsyncSession = Depends(get_db)):
    query = select(LinkageRule).where(LinkageRule.id == item_id, LinkageRule.deleted_at.is_(None))
    result = await db.execute(query)
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Linkage rule not found")

    for key, value in data.model_dump().items():
        setattr(rule, key, value)

    await db.commit()
    await db.refresh(rule)
    return LinkageRuleResponse.model_validate(rule)


@router.delete("/{item_id}")
async def delete_linkage_rule(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(LinkageRule).where(LinkageRule.id == item_id, LinkageRule.deleted_at.is_(None))
    result = await db.execute(query)
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Linkage rule not found")

    rule.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "Linkage rule deleted"}


@router.post("/{item_id}/enable")
async def enable_linkage_rule(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(LinkageRule).where(LinkageRule.id == item_id, LinkageRule.deleted_at.is_(None))
    result = await db.execute(query)
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Linkage rule not found")
    rule.status = "active"
    await db.commit()
    await db.refresh(rule)
    return {"id": rule.id, "status": rule.status}


@router.post("/{item_id}/disable")
async def disable_linkage_rule(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(LinkageRule).where(LinkageRule.id == item_id, LinkageRule.deleted_at.is_(None))
    result = await db.execute(query)
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Linkage rule not found")
    rule.status = "inactive"
    await db.commit()
    await db.refresh(rule)
    return {"id": rule.id, "status": rule.status}


deployment_router = APIRouter(prefix="/deployment-schedules", tags=["deployment-schedules"])


@deployment_router.get("", response_model=dict)
async def list_deployment_schedules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    deployment_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(DeploymentSchedule).where(DeploymentSchedule.deleted_at.is_(None))

    if deployment_id:
        query = query.where(DeploymentSchedule.deployment_id == deployment_id)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": [DeploymentScheduleResponse.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@deployment_router.get("/{item_id}", response_model=DeploymentScheduleResponse)
async def get_deployment_schedule(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(DeploymentSchedule).where(DeploymentSchedule.id == item_id, DeploymentSchedule.deleted_at.is_(None))
    result = await db.execute(query)
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Deployment schedule not found")
    return DeploymentScheduleResponse.model_validate(schedule)


@deployment_router.post("", response_model=DeploymentScheduleResponse)
async def create_deployment_schedule(data: DeploymentScheduleRequest, db: AsyncSession = Depends(get_db)):
    schedule = DeploymentSchedule(**data.model_dump())
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    return DeploymentScheduleResponse.model_validate(schedule)


@deployment_router.put("/{item_id}", response_model=DeploymentScheduleResponse)
async def update_deployment_schedule(item_id: int, data: DeploymentScheduleRequest, db: AsyncSession = Depends(get_db)):
    query = select(DeploymentSchedule).where(DeploymentSchedule.id == item_id, DeploymentSchedule.deleted_at.is_(None))
    result = await db.execute(query)
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Deployment schedule not found")

    for key, value in data.model_dump().items():
        setattr(schedule, key, value)

    await db.commit()
    await db.refresh(schedule)
    return DeploymentScheduleResponse.model_validate(schedule)


@deployment_router.delete("/{item_id}")
async def delete_deployment_schedule(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(DeploymentSchedule).where(DeploymentSchedule.id == item_id, DeploymentSchedule.deleted_at.is_(None))
    result = await db.execute(query)
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Deployment schedule not found")

    schedule.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "Deployment schedule deleted"}