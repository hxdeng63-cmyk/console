"""
DeploymentSyncService: synchronizes Deployments from VideoSetting changes.

For each camera (device_id) referenced by a VideoSetting, this service ensures
that exactly one Deployment exists for every unique traffic module selected via
VideoSetting.event_types. Deployments for deselected modules are stopped and
soft-deleted.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.algorithm import Algorithm
from app.models.deployment import Deployment
from app.models.deployment_device import DeploymentDevice
from app.models.device import Device
from app.models.event_type import EventType
from app.models.video_setting import VideoSetting
from app.services.process_monitor import ProcessMonitor
from app.services.stream_url_resolver import resolve_stream_url_for_device

logger = logging.getLogger(__name__)


class DeploymentSyncService:
    """Sync Deployment records with VideoSetting event types."""

    def __init__(self) -> None:
        self._monitor = ProcessMonitor()

    async def sync_for_video_setting(
        self,
        db: AsyncSession,
        video_setting: VideoSetting,
    ) -> None:
        """
        Create/start or stop/delete Deployments for all devices in a VideoSetting.

        The operation is best-effort per module: a failure to start one module
        does not roll back already-started modules. A subsequent VideoSetting
        save will retry failed modules.
        """
        device_ids = video_setting.device_ids or []
        event_type_ids = video_setting.event_types or []

        if not device_ids:
            logger.info("VideoSetting %s has no device_ids; nothing to sync", video_setting.id)
            return

        # Map selected event types to unique module names.
        event_types = await self._fetch_event_types(db, event_type_ids)
        unique_modules = {et.module_name for et in event_types if et.module_name}

        traffic_algorithm = await db.execute(
            select(Algorithm).where(Algorithm.name == "traffic", Algorithm.deleted_at.is_(None))
        )
        traffic_algorithm = traffic_algorithm.scalar_one_or_none()
        if traffic_algorithm is None:
            logger.error("Traffic algorithm not found; cannot sync deployments")
            return

        for device_id in device_ids:
            await self._sync_device(
                db,
                device_id=device_id,
                module_names=unique_modules,
                traffic_algorithm_id=traffic_algorithm.id,
            )

    async def delete_for_video_setting(
        self,
        db: AsyncSession,
        video_setting: VideoSetting,
    ) -> None:
        """Stop and soft-delete all Deployments tied to the VideoSetting's devices."""
        device_ids = video_setting.device_ids or []
        if not device_ids:
            return

        for device_id in device_ids:
            deployments = await self._get_active_deployments_for_device(db, device_id)
            for deployment in deployments:
                await self._stop_and_delete_deployment(db, deployment)

    async def cleanup_uncovered_deployments(
        self,
        db: AsyncSession,
    ) -> None:
        """Stop and soft-delete deployments not covered by any VideoSetting.

        This removes stale deployments for devices that are no longer in any
        VideoSetting.device_ids, as well as deployments with a NULL device_id.
        """
        settings = await db.execute(
            select(VideoSetting).where(
                VideoSetting.deleted_at.is_(None),
                VideoSetting.status.is_(True),
            )
        )
        covered_device_ids: set[int] = set()
        for setting in settings.scalars().all():
            device_ids = setting.device_ids or []
            if isinstance(device_ids, str):
                try:
                    device_ids = json.loads(device_ids)
                except Exception:
                    device_ids = []
            for device_id in device_ids:
                try:
                    covered_device_ids.add(int(device_id))
                except (TypeError, ValueError):
                    continue

        stmt = (
            select(Deployment)
            .where(Deployment.deleted_at.is_(None))
            .where(
                (Deployment.device_id.is_(None))
                | (~Deployment.device_id.in_(covered_device_ids))
            )
        )
        result = await db.execute(stmt)
        deployments = list(result.scalars().all())
        if not deployments:
            logger.info("No uncovered deployments to clean up")
            return

        for deployment in deployments:
            await self._stop_and_delete_deployment(db, deployment)
        logger.info("Cleaned up %s uncovered deployment(s)", len(deployments))

    async def _fetch_event_types(
        self,
        db: AsyncSession,
        event_type_ids: Iterable[int],
    ) -> list[EventType]:
        ids = [int(eid) for eid in event_type_ids]
        if not ids:
            return []
        result = await db.execute(
            select(EventType).where(
                EventType.id.in_(ids),
                EventType.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def _sync_device(
        self,
        db: AsyncSession,
        device_id: int,
        module_names: set[str],
        traffic_algorithm_id: int,
    ) -> None:
        device = await db.get(Device, device_id)
        if device is None or device.deleted_at is not None:
            logger.warning("Device %s not found or deleted; skipping deployment sync", device_id)
            return

        stream_url = await resolve_stream_url_for_device(db, device_id)
        if not stream_url:
            logger.error("No stream URL resolved for device %s; skipping", device_id)
            return

        # Lock existing deployments for this device to avoid races.
        existing_deployments = await self._get_active_deployments_for_device(
            db, device_id, for_update=True
        )
        existing_by_module = {d.module_name: d for d in existing_deployments if d.module_name}

        # Start/create or restart deployments for selected modules.
        for module_name in sorted(module_names):
            existing = existing_by_module.get(module_name)
            if existing is not None:
                if await self._is_deployment_healthy(existing):
                    # Healthy and running; leave it.
                    continue
                # Deployment is in a non-running state; restart it.
                logger.info(
                    "Restarting unhealthy deployment %s (status=%s) for device=%s module=%s",
                    existing.id,
                    existing.algorithm_status,
                    device_id,
                    module_name,
                )
                await self._restart_deployment_process(db, existing, stream_url)
                continue

            deployment = await self._create_deployment(
                db,
                device=device,
                module_name=module_name,
                traffic_algorithm_id=traffic_algorithm_id,
                stream_url=stream_url,
            )
            if deployment is None:
                # Duplicate race or DB error; skip.
                continue

            await self._start_deployment_process(db, deployment, stream_url)

        # Stop/delete deployments for deselected modules.
        for module_name, deployment in existing_by_module.items():
            if module_name in module_names:
                continue
            await self._stop_and_delete_deployment(db, deployment)

    async def _create_deployment(
        self,
        db: AsyncSession,
        device: Device,
        module_name: str,
        traffic_algorithm_id: int,
        stream_url: str,
    ) -> Optional[Deployment]:
        device_id = device.id
        stream_id = f"{device_id}_{module_name}"
        config_json = {
            "stream_map": {str(device_id): stream_id},
            "module_config": {},
            "video_path": stream_url,
        }

        deployment = Deployment(
            name=f"traffic_{module_name}_{device_id}",
            algorithm_id=traffic_algorithm_id,
            module_name=module_name,
            device_id=device_id,
            algorithm_status="pending",
            status="active",
            config_json=config_json,
            org_id=device.org_id,
            region_id=device.region_id,
        )
        db.add(deployment)

        try:
            await db.flush()
        except IntegrityError as exc:
            logger.warning(
                "Race creating Deployment for (device=%s, module=%s): %s",
                device_id,
                module_name,
                exc,
            )
            await db.rollback()
            return None

        # Keep DeploymentDevice join table in sync with denormalized device_id.
        db.add(DeploymentDevice(deployment_id=deployment.id, device_id=device_id))
        await db.commit()
        await db.refresh(deployment)
        logger.info(
            "Created Deployment %s for device=%s module=%s", deployment.id, device_id, module_name
        )
        return deployment

    async def _start_deployment_process(
        self,
        db: AsyncSession,
        deployment: Deployment,
        stream_url: str,
    ) -> None:
        token = self._monitor.generate_token()
        deployment.deployment_token = token
        await db.commit()

        try:
            result = await self._monitor.start(
                module_name=deployment.module_name,
                video_path=stream_url,
                deployment_id=deployment.id,
                stream_id=deployment.config_json.get("stream_map", {}).get(
                    str(deployment.device_id)
                )
                if deployment.config_json
                else str(deployment.device_id),
                config=deployment.config_json.get("module_config") if deployment.config_json else {},
                log_path=f"logs/traffic_{deployment.id}.log",
                deployment_token=token,
            )
        except Exception as exc:
            logger.exception(
                "Failed to start module %s for deployment %s: %s",
                deployment.module_name,
                deployment.id,
                exc,
            )
            deployment.algorithm_status = "error"
            deployment.stopped_at = datetime.utcnow()
            await db.commit()
            return

        deployment.pid = result["pid"]
        deployment.algorithm_status = "running"
        deployment.started_at = datetime.utcnow()
        deployment.stopped_at = None
        deployment.exit_code = None
        await db.commit()
        logger.info(
            "Started module %s for deployment %s (pid=%s)",
            deployment.module_name,
            deployment.id,
            result["pid"],
        )

    async def _restart_deployment_process(
        self,
        db: AsyncSession,
        deployment: Deployment,
        stream_url: str,
    ) -> None:
        """Stop a non-running deployment's tracked process and start a fresh one."""
        # Best-effort stop: ignore errors if no tracked process exists.
        try:
            await self._monitor.stop(deployment.id)
        except Exception:
            logger.exception(
                "Error stopping prior process for deployment %s before restart", deployment.id
            )

        # Refresh config_json in case stream_url changed.
        config_json = dict(deployment.config_json or {})
        config_json["video_path"] = stream_url
        deployment.config_json = config_json

        await self._start_deployment_process(db, deployment, stream_url)

    async def _is_deployment_healthy(self, deployment: Deployment) -> bool:
        """Return True if deployment is in a running state with an alive process."""
        if deployment.algorithm_status != "running":
            return False
        if not self._monitor.is_process_running(deployment.id):
            return False
        return True

    async def _stop_and_delete_deployment(
        self,
        db: AsyncSession,
        deployment: Deployment,
    ) -> None:
        try:
            await self._monitor.stop(deployment.id)
        except Exception:
            logger.exception("Error stopping deployment %s", deployment.id)

        deployment.algorithm_status = "stopped"
        deployment.pid = None
        deployment.stopped_at = datetime.utcnow()
        deployment.deleted_at = datetime.utcnow()
        await db.commit()
        logger.info("Stopped and soft-deleted deployment %s", deployment.id)

    async def _get_active_deployments_for_device(
        self,
        db: AsyncSession,
        device_id: int,
        for_update: bool = False,
    ) -> list[Deployment]:
        stmt = (
            select(Deployment)
            .where(
                Deployment.device_id == device_id,
                Deployment.deleted_at.is_(None),
            )
        )
        if for_update:
            stmt = stmt.with_for_update()
        result = await db.execute(stmt)
        return list(result.scalars().all())
