from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.data_source import DataSource
from app.models.device_stream import DeviceStream


async def resolve_stream_url_for_device(db: AsyncSession, device_id: int) -> str | None:
    """查找设备可用的视频源地址（本地文件或流 URL）。

    查找优先级：
    1. DataSource 中的本地文件（rtsp_url 以 docs/ 或 / 开头，或 access_type == '本地'）
    2. DeviceStream 中的流地址（按 is_primary 降序）
    3. DataSource 中的其他 rtsp_url
    """
    stmt = (
        select(DataSource)
        .where(
            DataSource.device_id == device_id,
            DataSource.deleted_at.is_(None),
            DataSource.rtsp_url.isnot(None),
        )
        .limit(1)
    )
    result = await db.execute(stmt)
    ds = result.scalar_one_or_none()
    if ds and ds.rtsp_url:
        url = ds.rtsp_url
        atype = (ds.access_type or "").lower()
        if url.startswith("docs/") or url.startswith("/") or atype == "本地":
            return url

    stmt = (
        select(DeviceStream)
        .where(
            DeviceStream.device_id == device_id,
            DeviceStream.deleted_at.is_(None),
            DeviceStream.stream_url.isnot(None),
        )
        .order_by(DeviceStream.is_primary.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    stream = result.scalar_one_or_none()
    if stream and stream.stream_url:
        return stream.stream_url

    if ds and ds.rtsp_url:
        return ds.rtsp_url

    return None
