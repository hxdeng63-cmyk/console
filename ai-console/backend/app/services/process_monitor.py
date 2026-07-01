"""DeploymentReconciler — traffic-api 化后的 reconcile 工具。

traffic-api 改造后，业务职责（start/stop/callback/watchdog）已迁出到
`app.services.traffic_api_client`。本类仅保留 reconcile() 用于同步
algorithm_status；旧名 ProcessMonitor 作为别名以兼容历史 import。
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional


logger = logging.getLogger(__name__)


# ---- 业务常量（保留用于入参校验） ---------------------------------

# traffic-api 接受主名或别名（API_SERVICE(1).md L873-884）。
# 此处仅保留我们后端 start 入参校验用的主名集合；traffic-api 端别名表见文档。
TRAFFIC_MODULE_WHITELIST = {
    "traffic",
    "traffic_jam",
    "vehicle_counting",
    "reverse",
    "reverse_detection",
    "pedestrian",
    "pedestrian_intrusion",
    "accident",
    "accident_detection",
    "vest",
    "vest_detection",
}


class DeploymentReconciler:
    """单例 reconcile 工具：调 traffic-api /status 同步 algorithm_status。"""

    _instance: Optional["DeploymentReconciler"] = None
    _lock: asyncio.Lock = asyncio.Lock()

    def __new__(cls) -> "DeploymentReconciler":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

    async def reconcile(self, db: Any) -> None:
        """traffic-api 化 reconcile：调 traffic_api_client.status 同步 algorithm_status。

        语义区分（关键）：
          - traffic-api 200 + status=running/pending/stopping → DB 保持
          - traffic-api 200 + status=stopped → DB 标 stopped
          - traffic-api 200 + status=crashed → DB 标 crashed
          - traffic-api 200 + status=completed → DB 标 completed
          - traffic-api 404 → DB 标 unknown（traffic-api 重启后任务记录丢失）
        """
        from datetime import datetime as _dt
        from sqlalchemy import select, update
        from app.models.deployment import Deployment
        from app.services.traffic_api_client import (
            TrafficApiAuthError,
            TrafficApiServerError,
            TrafficApiUnavailableError,
            get_traffic_api_client,
        )

        client = get_traffic_api_client()
        try:
            rows = (await db.execute(
                select(Deployment.id, Deployment.algorithm_status, Deployment.pid)
                .where(
                    Deployment.algorithm_status == "running",
                    Deployment.deleted_at.is_(None),
                )
            )).all()
        except Exception:
            logger.exception("reconcile: failed to query deployments")
            return

        to_update: list[tuple[int, str, int | None]] = []
        for deployment_id, cur_status, pid in rows:
            try:
                traffic_status = await client.status(deployment_id)
            except (TrafficApiUnavailableError, TrafficApiAuthError, TrafficApiServerError) as exc:
                # traffic-api 暂时不可用：保留原状态，不在启动时 cascade crash
                logger.warning(
                    "reconcile: traffic-api unavailable for deployment %s: %s", deployment_id, exc
                )
                continue

            if traffic_status is None:
                # 404: traffic-api 重启后任务记录丢失
                to_update.append((deployment_id, "unknown", None))
                continue

            s = (traffic_status.get("status") or "").lower()
            live_pid = traffic_status.get("pid") or pid
            if s == "running":
                to_update.append((deployment_id, "running", live_pid))
            elif s in ("pending", "stopping"):
                to_update.append((deployment_id, "pending", live_pid))
            elif s == "stopped":
                to_update.append((deployment_id, "stopped", None))
            elif s == "crashed":
                to_update.append((deployment_id, "crashed", None))
            elif s == "completed":
                to_update.append((deployment_id, "completed", None))
            # 未知状态：保留 DB 原值

        if to_update:
            try:
                for dep_id, new_status, new_pid in to_update:
                    await db.execute(
                        update(Deployment)
                        .where(Deployment.id == dep_id)
                        .values(
                            algorithm_status=new_status,
                            pid=new_pid,
                            stopped_at=(_dt.utcnow() if new_status in {"stopped", "crashed", "completed", "unknown"} else None),
                        )
                    )
                await db.commit()
                logger.info("reconcile: synced %d deployment(s) with traffic-api", len(to_update))
            except Exception:
                logger.exception("reconcile: failed to update %d deployments", len(to_update))
                try:
                    await db.rollback()
                except Exception:
                    pass
        else:
            logger.info("reconcile: 0 deployments need status sync")


# 兼容旧 import（deployments.py / deployment_sync.py 仍在用）
ProcessMonitor = DeploymentReconciler