"""流代理：traffic-api 主路径 + 本地文件/HTTP 兜底。"""
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.async_tasks import async_task_manager
from app.core.database import AsyncSessionLocal, get_db
from app.models.data_source import DataSource
from app.services.stream_url_resolver import resolve_stream_url_for_device
from app.services.traffic_api_client import (
    TrafficApiAuthError,
    TrafficApiNotFoundError,
    TrafficApiUnavailableError,
    get_traffic_api_client,
)

router = APIRouter(prefix="/stream", tags=["stream"])

_PROJECT_ROOT = Path(__file__).resolve().parents[5]


async def _find_stream_url(device_id: int, db: AsyncSession) -> tuple[str | None, str | None]:
    """查找设备的流地址，优先本地文件，再 DeviceStream，最后 DataSource。返回 (stream_url, access_type)"""
    stream_url = await resolve_stream_url_for_device(db, device_id)
    if not stream_url:
        return None, None

    # 本地文件路径判断
    if stream_url.startswith("docs/") or stream_url.startswith("/"):
        return stream_url, "本地"

    # 查询 DataSource 以获取 access_type
    stmt = (
        select(DataSource)
        .where(
            DataSource.device_id == device_id,
            DataSource.deleted_at.is_(None),
            DataSource.rtsp_url == stream_url,
        )
        .limit(1)
    )
    result = await db.execute(stmt)
    ds = result.scalar_one_or_none()
    access_type = (ds.access_type or "").lower() if ds else ""

    if access_type in ("http/https", "http", "https") or stream_url.startswith("http://") or stream_url.startswith("https://"):
        return stream_url, "http"

    return stream_url, access_type or "rtsp"


@router.get("/device/{device_id}/flv")
async def get_device_flv_url(device_id: int, db: AsyncSession = Depends(get_db)):
    """根据设备 ID 获取播放地址：先 traffic-api，回退到本地文件 / HTTP 直连。"""
    result = await _resolve_device_stream(device_id, db)
    if result is None:
        raise HTTPException(status_code=404, detail="该设备无流地址配置")
    return result


@router.post("/devices/register", response_model=dict)
async def register_devices(
    request: dict,
    db: AsyncSession = Depends(get_db),
):
    """批量注册设备流路径：转发到 traffic-api（traffic-api 内部建 HLS）。
    立即返回 task_id，由后台任务汇总 progress。"""
    device_ids = request.get("device_ids", [])
    if not device_ids:
        raise HTTPException(status_code=400, detail="device_ids 不能为空")

    task_id = async_task_manager.create_task(
        status="pending",
        extra={"total": len(device_ids), "results": []},
    )
    async_task_manager.run_task(task_id, lambda tid: _run_register_devices_task(tid, list(device_ids)))
    return {"task_id": task_id, "status": "pending"}


@router.get("/devices/register/status/{task_id}", response_model=dict)
async def get_register_devices_status(task_id: str):
    """查询批量流注册任务的进度与结果。"""
    task = await async_task_manager.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


async def _run_register_devices_task(task_id: str, device_ids: list) -> None:
    """后台执行批量流注册：转发 traffic-api register_streams，逐设备用 _resolve_device_stream 兜底。"""
    await async_task_manager.update_task(task_id, "running")

    client = get_traffic_api_client()

    async with AsyncSessionLocal() as db:
        # traffic-api /stream/devices/register 要求每条 device 必带 rtsp_url（不带会静默丢弃）。
        # 从 DataSource 查 5 个 device 的 rtsp_url，缺失的也保留（traffic-api 会自己 404）。
        raw_int_ids = [int(d) for d in device_ids if str(d).isdigit()]
        ds_rows = await db.execute(
            select(DataSource.device_id, DataSource.rtsp_url).where(
                DataSource.device_id.in_(raw_int_ids),
                DataSource.deleted_at.is_(None),
            )
        )
        rtsp_map: dict[int, str] = {}
        for raw_id, rtsp_url in ds_rows.all():
            rtsp_map[raw_id] = rtsp_url
        devices_payload = [
            {"device_id": did, "rtsp_url": rtsp_map[did]}
            for did in raw_int_ids
            if did in rtsp_map
        ]

        results: list[dict] = []
        done = 0
        failed = 0

        for raw_id in device_ids:
            entry: dict = {
                "device_id": raw_id,
                "success": False,
                "error": None,
                "flv_url": None,
                "source_type": None,
                "stream_name": None,
            }
            try:
                device_id = int(raw_id)
            except (ValueError, TypeError):
                entry["error"] = "无效的设备 ID"
                failed += 1
                results.append(entry)
                await _publish_stream_progress(task_id, device_ids, done, failed, results)
                continue

            entry["device_id"] = device_id
            try:
                info = await _resolve_device_stream(device_id, db)
                if info is None:
                    entry["error"] = "该设备无流地址配置"
                    entry["flv_url"] = ""
                    entry["source_type"] = "unavailable"
                    failed += 1
                else:
                    entry.update({
                        "success": True,
                        "flv_url": info["flv_url"],
                        "source_type": info["source_type"],
                        "stream_name": info.get("stream_name"),
                    })
                    done += 1
            except HTTPException as e:
                entry["error"] = e.detail
                failed += 1
            except Exception as e:
                entry["error"] = f"注册失败: {str(e)}"
                failed += 1

            results.append(entry)
            await _publish_stream_progress(task_id, device_ids, done, failed, results)

        # 转发到 traffic-api：traffic-api 端在收到 list 后会自行注册 RTSP→HLS。
        # 我们本地不等待 traffic-api 返回（注册是幂等的，前端拿到 flv_url 即可播放）。
        if devices_payload:
            try:
                await client.register_streams(devices_payload)
            except Exception:
                # traffic-api 暂时不可用时，本地兜底返回的 flv_url 仍可工作；不抛给前端。
                logging.warning("traffic-api register_streams 调用失败，继续走本地兜底")

        await async_task_manager.update_task(
            task_id,
            "completed",
            {
                "total": len(device_ids),
                "done": done,
                "failed": failed,
                "results": list(results),
            },
        )


async def _publish_stream_progress(
    task_id: str,
    device_ids: list,
    done: int,
    failed: int,
    results: list[dict],
) -> None:
    await async_task_manager.update_task(
        task_id,
        "running",
        {
            "total": len(device_ids),
            "done": done,
            "failed": failed,
            "results": list(results),
        },
    )


async def _resolve_device_stream(device_id: int, db: AsyncSession) -> dict | None:
    """解析设备流地址：先 traffic-api；traffic-api 404 时回退 _local_file_fallback。

    直播流 RTSP/RTMP 由 traffic-api 在收到 /start 后内部注册到其 HLS endpoint；
    本接口直接读 traffic-api /flv 拿到 m3u8 路径。
    """
    client = get_traffic_api_client()
    try:
        info = await client.device_flv_url(device_id)
    except (TrafficApiNotFoundError, TrafficApiAuthError, TrafficApiUnavailableError):
        info = None
    if isinstance(info, dict) and info.get("flv_url"):
        return {
            "device_id": device_id,
            "stream_name": info.get("stream_name"),
            "flv_url": info["flv_url"],
            "rtsp_url": info.get("rtsp_url"),
            "source_type": info.get("source_type", "stream"),
        }

    # 兜底：本地文件 / HTTP 直连
    return await _local_file_fallback(device_id, db)


async def _local_file_fallback(device_id: int, db: AsyncSession) -> dict | None:
    """traffic-api 不可用时，从 resolve_stream_url_for_device 解析本地文件 / HTTP 直连 URL。

    对 RTSP 源，若 data/monitoring/ 下有对应 device 的 mp4 兜底素材，
    也直接返回 mp4 路径，避免被 traffic-api 鉴权阻塞。
    """
    stream_url, access_type = await _find_stream_url(device_id, db)
    if not stream_url:
        return None

    # 本地文件路径：直接返回文件 URL
    # Per migration: stream_url is now /data/...  (legacy docs/ or /uploads/ also accepted for safety)
    if (
        stream_url.startswith("docs/")
        or stream_url.startswith("/data/")
        or stream_url.startswith("/uploads/")
        or access_type == "本地"
    ):
        if stream_url.startswith("docs/"):
            flv_url = f"/data/{stream_url[5:]}"
        elif stream_url.startswith("/uploads/"):
            flv_url = f"/data/{stream_url[len('/uploads/'):]}"
        else:
            # /data/... or already an absolute /data/ URL
            flv_url = stream_url
        # Don't fail on file_path.exists() — the frontend can handle 404.
        # The main.py /data/ StaticFiles mount serves whatever is present.

        return {
            "device_id": device_id,
            "stream_name": None,
            "flv_url": flv_url,
            "rtsp_url": stream_url,
            "source_type": "local",
        }

    # RTSP 源：若 data/monitoring/<device_id>.mp4 存在（兜底素材），
    # 直接返回 mp4 静态路径，前端 VideoStage 会走 MonitoringVideoPlayer（带 controls）。
    # Per migration: public/monitoring/ → data/monitoring/
    static_mp4 = (
        _PROJECT_ROOT / "data" / "monitoring" / f"device_{device_id}.mp4"
    )
    if static_mp4.exists():
        return {
            "device_id": device_id,
            "stream_name": None,
            "flv_url": f"/data/monitoring/device_{device_id}.mp4",
            "rtsp_url": stream_url,
            "source_type": "local",
        }

    # HTTP/HTTPS 流：直接返回原始地址
    if access_type in ("http/https", "http", "https") or stream_url.startswith("http://") or stream_url.startswith("https://"):
        return {
            "device_id": device_id,
            "stream_name": None,
            "flv_url": stream_url,
            "rtsp_url": stream_url,
            "source_type": "http",
        }

    # RTSP/RTMP 在无 traffic-api 情况下无法播放，返回 None
    return None
