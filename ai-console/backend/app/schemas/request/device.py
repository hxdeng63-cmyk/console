from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from typing import Optional


class DeviceRequest(BaseModel):
    device_code: str
    name: str
    status: str = "active"
    access_type: str = "direct"
    device_type: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    region_id: Optional[int] = None
    org_id: Optional[int] = None
    memory_usage: Optional[float] = None
    disk_size: Optional[int] = None
    disk_usage: Optional[float] = None
    remark: Optional[str] = None


class DeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_code: str
    name: str
    status: str
    access_type: str
    device_type: Optional[str]
    longitude: Optional[Decimal]
    latitude: Optional[Decimal]
    region_id: Optional[int]
    org_id: Optional[int]
    memory_usage: Optional[Decimal]
    disk_size: Optional[int]
    disk_usage: Optional[Decimal]
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class DeviceGroupRequest(BaseModel):
    group_code: Optional[str] = None
    name: str
    device_count: int = 0
    remark: Optional[str] = None
    region_id: Optional[int] = None


class DeviceGroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    group_code: Optional[str]
    name: str
    device_count: int
    remark: Optional[str]
    region_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


