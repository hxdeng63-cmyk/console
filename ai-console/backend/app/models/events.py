"""
SQLAlchemy event listeners for WarningEvent -> File auto-creation.
单独文件避免 file.py 和 warning_event.py 之间的循环导入。
"""
from datetime import datetime, timezone
import os

from sqlalchemy import event

from app.models.file import File, FileSourceType
from app.models.warning_event import WarningEvent


def _build_file_record(target, url: str, source_type: FileSourceType) -> dict:
    """构建 File 记录的字典。"""
    return {
        'warning_event_id': target.id,
        'device_id': target.device_id,
        'source_type': source_type.value,
        'file_name': os.path.basename(url) or (source_type.value + '.jpg'),
        'file_type': 'image' if source_type == FileSourceType.WARNING_EVENT_IMAGE else 'video',
        'url': url,
        'storage_path': url,
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc),
    }


@event.listens_for(WarningEvent, 'after_insert')
def create_file_records_on_insert(mapper, connection, target):
    """WarningEvent 插入后自动创建 File 记录。"""
    file_table = File.__table__
    files_to_create = []

    if target.image_url:
        files_to_create.append(_build_file_record(
            target, target.image_url, FileSourceType.WARNING_EVENT_IMAGE
        ))
    if target.video_url:
        files_to_create.append(_build_file_record(
            target, target.video_url, FileSourceType.WARNING_EVENT_VIDEO
        ))

    if files_to_create:
        connection.execute(file_table.insert(), files_to_create)


@event.listens_for(WarningEvent, 'after_update')
def sync_file_records_on_update(mapper, connection, target):
    """
    WarningEvent 更新后同步 File 记录。
    处理 image_url/video_url 的增删改。
    """
    file_table = File.__table__

    # 获取当前的 file 记录
    from sqlalchemy import select
    stmt = select(file_table.c.source_type).where(
        file_table.c.warning_event_id == target.id
    )
    existing = {row[0] for row in connection.execute(stmt).fetchall()}

    # 处理 image_url
    has_image = bool(target.image_url)
    image_exists = FileSourceType.WARNING_EVENT_IMAGE.value in existing
    if has_image and not image_exists:
        # 新增 image file
        connection.execute(file_table.insert(), [_build_file_record(
            target, target.image_url, FileSourceType.WARNING_EVENT_IMAGE
        )])
    elif has_image and image_exists:
        # 更新 image URL（如变更）
        connection.execute(
            file_table.update().where(
                file_table.c.warning_event_id == target.id,
                file_table.c.source_type == FileSourceType.WARNING_EVENT_IMAGE.value
            ), {
                'url': target.image_url,
                'storage_path': target.image_url,
                'file_name': os.path.basename(target.image_url) or 'image.jpg',
                'updated_at': datetime.now(timezone.utc),
            }
        )
    elif not has_image and image_exists:
        # 删除 image file
        connection.execute(
            file_table.delete().where(
                file_table.c.warning_event_id == target.id,
                file_table.c.source_type == FileSourceType.WARNING_EVENT_IMAGE.value
            )
        )

    # 处理 video_url（同理）
    has_video = bool(target.video_url)
    video_exists = FileSourceType.WARNING_EVENT_VIDEO.value in existing
    if has_video and not video_exists:
        connection.execute(file_table.insert(), [_build_file_record(
            target, target.video_url, FileSourceType.WARNING_EVENT_VIDEO
        )])
    elif has_video and video_exists:
        connection.execute(
            file_table.update().where(
                file_table.c.warning_event_id == target.id,
                file_table.c.source_type == FileSourceType.WARNING_EVENT_VIDEO.value
            ), {
                'url': target.video_url,
                'storage_path': target.video_url,
                'file_name': os.path.basename(target.video_url) or 'video.mp4',
                'updated_at': datetime.now(timezone.utc),
            }
        )
    elif not has_video and video_exists:
        connection.execute(
            file_table.delete().where(
                file_table.c.warning_event_id == target.id,
                file_table.c.source_type == FileSourceType.WARNING_EVENT_VIDEO.value
            )
        )
