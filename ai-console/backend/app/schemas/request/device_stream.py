from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class DeviceStreamRequest(BaseModel):
    device_id: int
    stream_type: str = "main"
    stream_url: Optional[str] = None
    push_url: Optional[str] = None
    resolution: Optional[str] = None
    fps: Optional[int] = None
    codec: Optional[str] = None
    is_primary: bool = False
    status: str = "active"


class DeviceStreamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    stream_type: str
    stream_url: Optional[str]
    push_url: Optional[str]
    resolution: Optional[str]
    fps: Optional[int]
    codec: Optional[str]
    is_primary: bool
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]