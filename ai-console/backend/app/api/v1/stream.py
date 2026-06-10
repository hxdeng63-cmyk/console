import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.device_stream import DeviceStream
from app.models.data_source import DataSource

router = APIRouter(prefix="/stream", tags=["stream"])

MEDIAMTX_API = "http://127.0.0.1:9997"
MEDIAMTX_HLS_BASE = "http://127.0.0.1:8888"


async def _find_stream_url(device_id: int, db: AsyncSession) -> tuple[str | None, str | None]:
    """查找设备的流地址，优先本地文件，再 DeviceStream，最后 DataSource。返回 (stream_url, access_type)"""

    # 1. 优先检查 DataSource 中的本地文件
    query = (
        select(DataSource)
        .where(
            DataSource.device_id == device_id,
            DataSource.deleted_at.is_(None),
            DataSource.rtsp_url.isnot(None),
        )
        .limit(1)
    )
    result = await db.execute(query)
    ds = result.scalar_one_or_none()
    if ds and ds.rtsp_url:
        url = ds.rtsp_url
        atype = (ds.access_type or "").lower()
        # 本地文件路径判断（URL 前缀优先，兼容旧"本地"类型）
        if url.startswith("docs/") or url.startswith("/"):
            return url, atype or "本地"
        # 兼容旧数据：access_type 为"本地"的也当作本地文件
        if atype == "本地":
            return url, "本地"

    # 2. 从 DeviceStream 查找真正的流地址
    query = (
        select(DeviceStream)
        .where(
            DeviceStream.device_id == device_id,
            DeviceStream.deleted_at.is_(None),
            DeviceStream.stream_url.isnot(None),
        )
        .order_by(DeviceStream.is_primary.desc())
        .limit(1)
    )
    result = await db.execute(query)
    stream = result.scalar_one_or_none()
    if stream and stream.stream_url:
        return stream.stream_url, "rtsp"

    # 3. 回退到 DataSource（非本地文件）
    if ds and ds.rtsp_url:
        return ds.rtsp_url, atype

    return None, None


@router.get("/device/{device_id}/flv")
async def get_device_flv_url(device_id: int, db: AsyncSession = Depends(get_db)):
    """根据设备 ID 获取播放地址"""
    stream_url, access_type = await _find_stream_url(device_id, db)

    if not stream_url:
        raise HTTPException(status_code=404, detail="该设备无流地址配置")

    # 本地文件路径：直接返回文件 URL，不经过 mediamtx
    if stream_url.startswith("docs/") or stream_url.startswith("/") or access_type == "本地":
        return {
            "device_id": device_id,
            "stream_name": None,
            "flv_url": f"/uploads/{stream_url}" if not stream_url.startswith("/") else stream_url,
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

    # RTSP/RTMP 流：通过 mediamtx 注册并返回 HLS 地址
    stream_name = f"device_{device_id}"
    hls_url = f"/stream/{stream_name}/index.m3u8"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{MEDIAMTX_API}/v3/config/paths/add/{stream_name}",
                json={
                    "source": stream_url,
                    "sourceOnDemand": False,
                },
            )
            if resp.status_code not in (200, 201, 204, 400):
                raise HTTPException(status_code=502, detail="注册流路径失败")
    except httpx.ConnectError:
        raise HTTPException(status_code=502, detail="mediamtx 服务不可用")

    return {
        "device_id": device_id,
        "stream_name": stream_name,
        "flv_url": hls_url,
        "rtsp_url": stream_url,
        "source_type": "stream",
    }
