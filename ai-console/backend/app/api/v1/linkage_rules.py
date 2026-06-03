from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.linkage_rule import LinkageRule
from app.models.linkage_rule_device import LinkageRuleDevice
from app.models.deployment_schedule import DeploymentSchedule
from app.schemas.request.linkage_rule import (
    LinkageRuleRequest,
    LinkageRuleResponse,
    DeploymentScheduleRequest,
    DeploymentScheduleResponse,
)

router = APIRouter(prefix="/linkage-rules", tags=["linkage-rules"])


async def _get_linkage_rule_or_404(db: AsyncSession, item_id: int) -> LinkageRule:
    query = select(LinkageRule).where(LinkageRule.id == item_id, LinkageRule.deleted_at.is_(None))
    result = await db.execute(query)
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Linkage rule not found")
    return rule


async def _get_selected_devices_for_rules(db: AsyncSession, rule_ids: list[int]) -> dict[int, list[int]]:
    """批量查询多个规则的关联设备 ID。"""
    if not rule_ids:
        return {}
    query = select(LinkageRuleDevice.linkage_rule_id, LinkageRuleDevice.device_id).where(
        LinkageRuleDevice.linkage_rule_id.in_(rule_ids)
    )
    result = await db.execute(query)
    mapping: dict[int, list[int]] = {}
    for rule_id, device_id in result.all():
        mapping.setdefault(rule_id, []).append(device_id)
    return mapping


async def _set_rule_devices(db: AsyncSession, rule_id: int, device_ids: list[int] | None) -> None:
    """替换规则的设备关联（先删后插）。"""
    await db.execute(delete(LinkageRuleDevice).where(LinkageRuleDevice.linkage_rule_id == rule_id))
    if device_ids:
        for did in device_ids:
            db.add(LinkageRuleDevice(linkage_rule_id=rule_id, device_id=did))


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

    rule_ids = [item.id for item in items]
    device_map = await _get_selected_devices_for_rules(db, rule_ids)

    return {
        "items": [
            {
                **LinkageRuleResponse.model_validate(item).model_dump(),
                "selected_devices": device_map.get(item.id, []),
            }
            for item in items
        ],
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
    rule = await _get_linkage_rule_or_404(db, item_id)
    device_map = await _get_selected_devices_for_rules(db, [item_id])
    data = {
        **LinkageRuleResponse.model_validate(rule).model_dump(),
        "selected_devices": device_map.get(item_id, []),
    }
    return LinkageRuleResponse.model_validate(data)


def _validate_push_channels(data: LinkageRuleRequest) -> None:
    """Validate push_target and channel config when TaskEdit-style push_channels is provided."""
    channels = data.push_channels
    if channels and isinstance(channels, dict) and channels.get("channel_type"):
        if not data.push_target:
            raise HTTPException(status_code=422, detail="推送目标不能为空")
        channel_type = channels["channel_type"]
        required_fields = {
            "wechat": ["app_id", "app_secret", "template_id"],
            "wechat_work": ["corp_id", "app_secret", "agent_id"],
            "dingtalk": ["app_key", "app_secret", "agent_id"],
            "sms": ["sms_id"],
        }
        fields = required_fields.get(channel_type)
        if fields:
            missing = [f for f in fields if not channels.get(f)]
            if missing:
                raise HTTPException(
                    status_code=422,
                    detail=f"{channel_type} 渠道缺少必填字段: {', '.join(missing)}"
                )


@router.post("", response_model=LinkageRuleResponse)
async def create_linkage_rule(data: LinkageRuleRequest, db: AsyncSession = Depends(get_db)):
    _validate_push_channels(data)
    dump = data.model_dump()
    selected_devices = dump.pop("selected_devices", None)
    rule = LinkageRule(**dump)
    db.add(rule)
    await db.commit()
    await db.refresh(rule)

    if selected_devices:
        await _set_rule_devices(db, rule.id, selected_devices)
        await db.commit()

    device_map = await _get_selected_devices_for_rules(db, [rule.id])
    result_data = {
        **LinkageRuleResponse.model_validate(rule).model_dump(),
        "selected_devices": device_map.get(rule.id, []),
    }
    return LinkageRuleResponse.model_validate(result_data)


@router.put("/{item_id}", response_model=LinkageRuleResponse)
async def update_linkage_rule(item_id: int, data: LinkageRuleRequest, db: AsyncSession = Depends(get_db)):
    _validate_push_channels(data)
    rule = await _get_linkage_rule_or_404(db, item_id)

    dump = data.model_dump()
    selected_devices = dump.pop("selected_devices", None)
    for key, value in dump.items():
        setattr(rule, key, value)

    await db.commit()
    await db.refresh(rule)

    if selected_devices is not None:
        await _set_rule_devices(db, item_id, selected_devices)
        await db.commit()

    device_map = await _get_selected_devices_for_rules(db, [item_id])
    result_data = {
        **LinkageRuleResponse.model_validate(rule).model_dump(),
        "selected_devices": device_map.get(item_id, []),
    }
    return LinkageRuleResponse.model_validate(result_data)


@router.delete("/{item_id}")
async def delete_linkage_rule(item_id: int, db: AsyncSession = Depends(get_db)):
    rule = await _get_linkage_rule_or_404(db, item_id)
    rule.deleted_at = datetime.utcnow()
    await db.execute(delete(LinkageRuleDevice).where(LinkageRuleDevice.linkage_rule_id == item_id))
    await db.commit()
    return {"message": "Linkage rule deleted"}


@router.post("/{item_id}/enable")
async def enable_linkage_rule(item_id: int, db: AsyncSession = Depends(get_db)):
    rule = await _get_linkage_rule_or_404(db, item_id)
    rule.status = "active"
    await db.commit()
    await db.refresh(rule)
    return {"id": rule.id, "status": rule.status}


@router.post("/{item_id}/disable")
async def disable_linkage_rule(item_id: int, db: AsyncSession = Depends(get_db)):
    rule = await _get_linkage_rule_or_404(db, item_id)
    rule.status = "inactive"
    await db.commit()
    await db.refresh(rule)
    return {"id": rule.id, "status": rule.status}


deployment_router = APIRouter(prefix="/deployment-schedules", tags=["deployment-schedules"])


async def _get_deployment_schedule_or_404(db: AsyncSession, item_id: int) -> DeploymentSchedule:
    query = select(DeploymentSchedule).where(DeploymentSchedule.id == item_id, DeploymentSchedule.deleted_at.is_(None))
    result = await db.execute(query)
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Deployment schedule not found")
    return schedule


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
    schedule = await _get_deployment_schedule_or_404(db, item_id)
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
    schedule = await _get_deployment_schedule_or_404(db, item_id)

    for key, value in data.model_dump().items():
        setattr(schedule, key, value)

    await db.commit()
    await db.refresh(schedule)
    return DeploymentScheduleResponse.model_validate(schedule)


@deployment_router.delete("/{item_id}")
async def delete_deployment_schedule(item_id: int, db: AsyncSession = Depends(get_db)):
    schedule = await _get_deployment_schedule_or_404(db, item_id)
    schedule.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "Deployment schedule deleted"}
