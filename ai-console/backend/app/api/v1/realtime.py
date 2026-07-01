"""实时指标聚合：traffic-api 推送后的 cache 视图。

traffic-api 是纯推理服务，无查询端点；推送结果经 callback 入库到 WarningEvent。
本端点反查 WarningEvent 取最近 frame 的真实指标（flow / jam），
并聚合今日事件统计 + 当前 active deployment 状态。
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.device import Device
from app.models.warning_event import WarningEvent
from app.models.event_type import EventType
from app.models.deployment import Deployment
from app.models.deployment_device import DeploymentDevice
from app.models.algorithm import Algorithm

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/realtime", tags=["realtime"])
BUSINESS_TZ = timezone(timedelta(hours=8))

# 图例颜色映射（与前端 EventDonutChart.vue 保持同步）
_LEGEND = {
    "jam":        ("#00FFCC", "拥堵"),
    "flow":       ("#0099FF", "车流"),
    "anomaly":    ("#00EAFF", "异常"),
    "reverse":    ("#FF9900", "逆行"),
    "pedestrian": ("#FF006E", "行人入侵"),
    "accident":   ("#FF4D4F", "事故"),
    "vest":       ("#52C41A", "反光衣"),
}

# 部署状态映射（与 useDashboardPolling 的 statusMap 同步）
_STATUS = {
    "running":   ("运行中", "online"),
    "stopped":   ("已停止", "offline"),
    "failed":    ("失败",   "warning"),
    "completed": ("已完成", "online"),
    "active":    ("运行中", "online"),
    "pending":   ("启动中", "warning"),
}


def _classify_road_level(is_jam: bool, confidence: float) -> tuple[int, str]:
    """jam 事件 → 道路等级。同 constants/roadLevel.ts 的 roadLevelFromJam。"""
    if is_jam:
        return 4, "拥堵"
    if confidence > 0.5:
        return 3, "缓慢"
    return 1, "畅通"


async def _latest_event_detail(db: AsyncSession, device_id: int, event_type_name: str) -> Optional[dict[str, Any]]:
    """取指定 device 上指定事件类型最近一条 WarningEvent 的 JSON detail。"""
    row = (await db.execute(
        select(WarningEvent.event_detail)
        .join(EventType, WarningEvent.event_type_id == EventType.id)
        .where(
            WarningEvent.device_id == device_id,
            WarningEvent.deleted_at.is_(None),
            EventType.name == event_type_name,
            EventType.deleted_at.is_(None),
        )
        .order_by(WarningEvent.report_time.desc())
        .limit(1)
    )).first()
    if not row:
        return None
    detail_str = row[0]
    if not detail_str:
        return None
    try:
        return json.loads(detail_str)
    except (ValueError, TypeError):
        logger.warning("realtime: invalid JSON in event_detail device=%s type=%s", device_id, event_type_name)
        return None


async def _today_event_stats(db: AsyncSession, device_id: int) -> dict[str, Any]:
    """今日事件统计：按 event_type.name 分组，使用 Asia/Shanghai 日界。"""
    today_start = datetime.now(BUSINESS_TZ).replace(hour=0, minute=0, second=0, microsecond=0).replace(tzinfo=None)
    rows = (await db.execute(
        select(EventType.name, func.count(WarningEvent.id))
        .join(WarningEvent, WarningEvent.event_type_id == EventType.id)
        .where(
            WarningEvent.device_id == device_id,
            WarningEvent.deleted_at.is_(None),
            WarningEvent.report_time >= today_start,
            EventType.deleted_at.is_(None),
        )
        .group_by(EventType.name)
    )).all()

    legend, total = [], 0
    for type_name, count in rows:
        if not type_name or count is None:
            continue
        color, label = _LEGEND.get(type_name, ("#0099FF", type_name))
        legend.append({"name": label, "value": int(count), "color": color})
        total += int(count)
    legend.sort(key=lambda x: x["value"], reverse=True)
    return {"total": total, "legend": legend}


async def _device_deployments(db: AsyncSession, device_id: int) -> list[dict[str, Any]]:
    """device 上的 deployment 列表（JOIN deployment_device / algorithm）。"""
    rows = (await db.execute(
        select(
            Deployment.id, Deployment.name, Deployment.module_name,
            Deployment.algorithm_status, Algorithm.name.label("algorithm_name"),
        )
        .join(DeploymentDevice, DeploymentDevice.deployment_id == Deployment.id)
        .outerjoin(Algorithm, Deployment.algorithm_id == Algorithm.id)
        .where(DeploymentDevice.device_id == device_id, Deployment.deleted_at.is_(None))
        .order_by(Deployment.id.desc())
    )).all()

    out = []
    for dep_id, name, module_name, algo_status, algorithm_name in rows:
        status = algo_status or "stopped"
        mapped = _STATUS.get(status, (status, "offline"))
        out.append({
            "name": name or f"deployment-{dep_id}",
            "algorithm": algorithm_name or module_name or "未知",
            "status": mapped[0],
            "statusClass": mapped[1],
        })
    return out


@router.get("/{device_id}/latest")
async def latest_realtime(device_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """实时指标聚合：单端点返回数字大屏所需的 4 类数据。

    - stats：traffic-api 最近推送的流量 / 拥堵
    - eventStats：今日事件总数 + 按类型分布（Asia/Shanghai 日界）
    - deployments：device 上的布控信息
    - asOf：服务端响应时间戳（前端可用于 staleness 检测）
    """
    # 1. 设备存在性校验
    exists = (await db.execute(
        select(Device.id).where(Device.id == device_id, Device.deleted_at.is_(None))
    )).scalar_one_or_none()
    if exists is None:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

    # 2. flow / jam 最近一条
    flow_detail = await _latest_event_detail(db, device_id, "flow")
    up_traffic = str(flow_detail["up_count"]) if flow_detail and "up_count" in flow_detail else "--"
    down_traffic = str(flow_detail["down_count"]) if flow_detail and "down_count" in flow_detail else "--"

    jam_detail = await _latest_event_detail(db, device_id, "jam")
    if jam_detail:
        road_level, road_level_text = _classify_road_level(
            bool(jam_detail.get("is_jam")), float(jam_detail.get("confidence") or 0.0)
        )
    else:
        road_level, road_level_text = 1, "畅通"

    # 3. 今日事件统计 + 4. active deployments
    event_stats = await _today_event_stats(db, device_id)
    deployments = await _device_deployments(db, device_id)

    return {
        "deviceId": device_id,
        "asOf": datetime.now(BUSINESS_TZ).isoformat(),
        "stats": {
            "avgSpeed": "--",  # traffic-api 暂未输出平均速度
            "upTraffic": up_traffic,
            "downTraffic": down_traffic,
            "roadLevel": road_level,
            "roadLevelText": road_level_text,
        },
        "eventStats": event_stats,
        "deployments": deployments,
    }