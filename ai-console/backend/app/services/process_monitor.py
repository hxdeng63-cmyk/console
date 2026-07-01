"""
ProcessMonitor (legacy 薄壳) — 保留以最小化 main.py / deployment_sync.py 改动。

traffic-api 改造后，本类的业务职责已迁出到 `app.services.traffic_api_client`：
  - 启停推理 → traffic_api_client.start / stop
  - 推流注册 → traffic_api_client.register_streams / device_flv_url
  - 推送 callback → traffic-api 子进程 → 用户后端（不再经过本进程）
  - GPU 调度 → traffic-api 端（MAX_CONCURRENT / MIN_GPU_MEM 等环境变量）

本类仅保留：
  - 单例骨架（__new__）
  - TRAFFIC_MODULE_WHITELIST：用于入参校验
  - reconcile(db)：改为查询 traffic-api /status 同步 algorithm_status 字段
  - register_status_callback / start_watchdog / stop_watchdog：保留签名以兼容 main.py；
    内部不再做任何事（traffic-api 主动 report，调用方通过 reconcile 或 polling 感知）

注：traffic-api 改造后无任何调用方再需要 token 生成器（callback_token 由 traffic-api 直接返回）。

未来重命名建议：`DeploymentReconciler`。
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable, Optional


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


class ProcessMonitor:
    """Legacy process monitor — 薄壳，仅保留 reconcile + 单例骨架。"""

    _instance: Optional["ProcessMonitor"] = None
    _lock: asyncio.Lock = asyncio.Lock()

    def __new__(cls) -> "ProcessMonitor":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self._status_callback: Optional[
            Callable[[int, str, Optional[int], Optional[str]], Awaitable[None]]
        ] = None

    # ---- 兼容旧调用点 -----------------------------------------

    def register_status_callback(
        self,
        callback: Callable[[int, str, Optional[int], Optional[str]], Awaitable[None]],
    ) -> None:
        """保留签名以便 main.py 不报错；实际不会触发（traffic-api 不通过 watchdog 回调）。"""
        self._status_callback = callback

    def start_watchdog(self) -> None:
        """占位实现：traffic-api 不再需要本地 watchdog。"""
        logger.info("ProcessMonitor.start_watchdog 是 noop（traffic-api 端负责）")

    async def stop_watchdog(self) -> None:
        """占位实现。"""
        return None

    # ---- 业务方法已迁出 ---------------------------------------

    async def start(self, *_args: Any, **_kwargs: Any) -> dict:
        raise NotImplementedError(
            "ProcessMonitor.start 已迁出到 app.services.traffic_api_client.start。"
            "请改用 traffic_api_client.start(deployment_id, payload)。"
        )

    async def stop(self, *_args: Any, **_kwargs: Any) -> dict:
        raise NotImplementedError(
            "ProcessMonitor.stop 已迁出到 app.services.traffic_api_client.stop。"
        )

    def is_deployment_running(self, deployment_id: int) -> bool:  # pragma: no cover - legacy
        return False

    def is_process_running(self, deployment_id: int) -> bool:  # pragma: no cover - legacy
        return False

    def get_pid(self, deployment_id: int) -> Optional[int]:  # pragma: no cover - legacy
        return None

    def get_exit_code(self, deployment_id: int) -> Optional[int]:  # pragma: no cover - legacy
        return None

    # ---- reconcile（保留 + 改造为 traffic-api 查询） --------

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
