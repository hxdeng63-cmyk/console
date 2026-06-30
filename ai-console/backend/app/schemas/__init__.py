from pydantic import BaseModel, Field, ConfigDict, computed_field, field_validator
from datetime import datetime
from typing import Optional, Any

from app.core.media import ensure_valid_media_url


class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list


class AlgorithmBase(BaseModel):
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    business_category: Optional[str] = None


class AlgorithmCreate(AlgorithmBase):
    pass


class AlgorithmUpdate(AlgorithmBase):
    pass


class AlgorithmEventItem(BaseModel):
    name: str
    description: Optional[str] = None
    module_name: Optional[str] = None


class AlgorithmResponse(AlgorithmBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    events: list[AlgorithmEventItem] = []

    class Config:
        from_attributes = True


class EventTypeBase(BaseModel):
    algorithm_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    category: str = "detection"
    severity: int = 1


class EventTypeCreate(EventTypeBase):
    pass


class EventTypeUpdate(EventTypeBase):
    pass


class EventTypeResponse(EventTypeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlgorithmServiceBase(BaseModel):
    service_id: Optional[str] = None
    service_name: Optional[str] = None
    service_code: Optional[str] = None
    service_ip: Optional[str] = None
    service_port: Optional[int] = None
    annotation_ip: Optional[str] = None
    annotation_port: Optional[int] = None
    status: str = "active"


class AlgorithmServiceCreate(AlgorithmServiceBase):
    pass


class AlgorithmServiceUpdate(AlgorithmServiceBase):
    pass


class AlgorithmServiceResponse(BaseModel):
    id: int
    service_id: Optional[str] = None
    service_name: Optional[str] = None
    service_code: Optional[str] = None
    service_ip: Optional[str] = None
    service_port: Optional[int] = None
    annotation_ip: Optional[str] = None
    annotation_port: Optional[int] = None
    status: str = "active"
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, item):
        # Convert INET types to strings
        data = item.__dict__.copy()
        if data.get('service_ip'):
            data['service_ip'] = str(data['service_ip'])
        if data.get('annotation_ip'):
            data['annotation_ip'] = str(data['annotation_ip'])
        return super().model_validate(data)


class TaskBase(BaseModel):
    task_name: str
    trigger_type: str = "cron"
    trigger_rule: Optional[str] = None
    algorithm_id: Optional[int] = None
    status: str = "active"


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskResponse(TaskBase):
    id: int
    last_run_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnnotationBase(BaseModel):
    deployment_id: Optional[int] = None
    device_id: Optional[int] = None
    name: Optional[str] = None
    type: str = "monitoring"
    polygon_json: Any = {}
    color: Optional[str] = None


class AnnotationCreate(AnnotationBase):
    pass


class AnnotationUpdate(AnnotationBase):
    pass


class AnnotationResponse(AnnotationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PresetBase(BaseModel):
    device_id: int
    name: str
    code: Optional[str] = None
    p: Optional[float] = None
    t: Optional[float] = None
    z: Optional[float] = None
    time_range_json: Optional[dict] = None


class PresetCreate(PresetBase):
    pass


class PresetUpdate(PresetBase):
    pass


class PresetResponse(PresetBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FileRecordBase(BaseModel):
    file_name: str
    file_size_bytes: Optional[int] = None
    duration_seconds: Optional[int] = None
    device_id: Optional[int] = None
    file_type: Optional[str] = None
    storage_path: Optional[str] = None
    url: Optional[str] = None
    warning_event_id: Optional[int] = None
    source_type: Optional[str] = None


class FileRecordCreate(FileRecordBase):
    pass


class FileRecordUpdate(FileRecordBase):
    pass


class FileRecordResponse(FileRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    @field_validator('url', 'storage_path', mode='before')
    @classmethod
    def validate_media_url(cls, v: Optional[str]) -> Optional[str]:
        return ensure_valid_media_url(v)

    class Config:
        from_attributes = True


class FirmwareBase(BaseModel):
    name: Optional[str] = None
    version: str
    applicable_version: Optional[str] = None
    force_upgrade: bool = False
    description: Optional[str] = None


class FirmwareCreate(FirmwareBase):
    pass


class FirmwareUpdate(FirmwareBase):
    pass


class FirmwareResponse(FirmwareBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DisposeTagBase(BaseModel):
    tag_name: str
    tag_color: Optional[str] = None
    usage_count: int = 0
    remark: Optional[str] = None


class DisposeTagCreate(DisposeTagBase):
    pass


class DisposeTagUpdate(DisposeTagBase):
    pass


class DisposeTagResponse(DisposeTagBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UIThemeBase(BaseModel):
    name: str
    platform: Optional[str] = None
    theme_color: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = False


class UIThemeCreate(UIThemeBase):
    pass


class UIThemeUpdate(UIThemeBase):
    pass


class UIThemeResponse(UIThemeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PopupSettingBase(BaseModel):
    config_json: dict = {}
    is_active: bool = True


class PopupSettingCreate(PopupSettingBase):
    pass


class PopupSettingUpdate(PopupSettingBase):
    pass


class PopupSettingResponse(PopupSettingBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AccessPlatformBase(BaseModel):
    name: str
    type: str
    version: Optional[str] = None
    device_count: int = 0
    status: str = "active"
    config_json: dict = {}


class AccessPlatformCreate(AccessPlatformBase):
    pass


class AccessPlatformUpdate(AccessPlatformBase):
    pass


class AccessPlatformResponse(AccessPlatformBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VideoSettingBase(BaseModel):
    org_id: int
    event_types: list = Field(default_factory=list)
    device_ids: list = Field(default_factory=list)
    record_duration_seconds: int = 10
    status: bool = True


class VideoSettingCreate(VideoSettingBase):
    pass


class VideoSettingUpdate(BaseModel):
    event_types: Optional[list] = None
    device_ids: Optional[list] = None
    record_duration_seconds: Optional[int] = None
    status: Optional[bool] = None


class VideoSettingResponse(BaseModel):
    id: int
    org_id: int
    event_types: list
    device_ids: list
    record_duration_seconds: int
    status: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    org_name: Optional[str] = None
    device_names: Optional[list] = None

    class Config:
        from_attributes = True


class CleanRecordBase(BaseModel):
    type: Optional[str] = None
    cutoff_time: Optional[datetime] = None
    status: str = "pending"
    progress: float = 0
    clean_size_bytes: int = 0


class CleanRecordCreate(CleanRecordBase):
    pass


class CleanRecordUpdate(BaseModel):
    type: Optional[str] = None
    cutoff_time: Optional[datetime] = None
    status: Optional[str] = None
    progress: Optional[float] = None
    clean_size_bytes: Optional[int] = None


class CleanRecordResponse(CleanRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    records_cleaned: int = 0
    dimension: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class MicroserviceBase(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    service_name: Optional[str] = None
    ip: Optional[str] = None
    port: Optional[int] = None
    status: str = "active"
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None


class MicroserviceCreate(MicroserviceBase):
    pass


class MicroserviceUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    service_name: Optional[str] = None
    ip: Optional[str] = None
    port: Optional[int] = None
    status: Optional[str] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None


class MicroserviceResponse(MicroserviceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LicenseBase(BaseModel):
    license_key: str
    type: Optional[str] = None
    device_limit: int = 0
    used_count: int = 0
    expire_date: Optional[datetime] = None
    status: str = "active"


class LicenseCreate(LicenseBase):
    pass


class LicenseUpdate(BaseModel):
    type: Optional[str] = None
    device_limit: Optional[int] = None
    used_count: Optional[int] = None
    expire_date: Optional[datetime] = None
    status: Optional[str] = None


class LicenseResponse(LicenseBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OperationLogBase(BaseModel):
    username: Optional[str] = None
    method: Optional[str] = None
    path: Optional[str] = None
    ip: Optional[str] = None
    status_code: Optional[int] = None
    result: Optional[str] = None
    description: Optional[str] = None
    action_time: Optional[datetime] = None


class OperationLogCreate(OperationLogBase):
    pass


class OperationLogUpdate(OperationLogBase):
    pass


class OperationLogResponse(OperationLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    @computed_field
    @property
    def operator(self) -> str:
        return self.username or ""

    @computed_field
    @property
    def real_name(self) -> str:
        return self.username or ""

    @computed_field
    @property
    def date(self) -> str:
        if self.action_time:
            return self.action_time.strftime("%Y-%m-%d %H:%M:%S")
        return "-"


class DataSourceBase(BaseModel):
    name: str
    status: str = "在线"
    rtsp_url: Optional[str] = None
    push_url: Optional[str] = None
    access_type: Optional[str] = None
    longitude: Optional[str] = None
    latitude: Optional[str] = None
    data_source_type: Optional[str] = None
    region: Optional[str] = None
    org: Optional[str] = None
    device: Optional[str] = None
    remark: Optional[str] = None
    memory_usage: Optional[int] = None
    disk_size: Optional[str] = None
    disk_usage: Optional[int] = None
    device_id: Optional[int] = None
    region_id: Optional[int] = None
    org_id: Optional[int] = None


class DataSourceCreate(DataSourceBase):
    pass


class DataSourceUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    rtsp_url: Optional[str] = None
    push_url: Optional[str] = None
    access_type: Optional[str] = None
    longitude: Optional[str] = None
    latitude: Optional[str] = None
    data_source_type: Optional[str] = None
    region: Optional[str] = None
    org: Optional[str] = None
    device: Optional[str] = None
    remark: Optional[str] = None
    memory_usage: Optional[int] = None
    disk_size: Optional[str] = None
    disk_usage: Optional[int] = None
    device_id: Optional[int] = None
    region_id: Optional[int] = None
    org_id: Optional[int] = None


class DataSourceResponse(DataSourceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    device_name: Optional[str] = None
    region_name: Optional[str] = None
    org_name: Optional[str] = None

    class Config:
        from_attributes = True


class PTWeightFileBase(BaseModel):
    name: str
    file_path: str
    description: Optional[str] = None


class PTWeightFileCreate(PTWeightFileBase):
    pass


class PTWeightFileUpdate(BaseModel):
    name: Optional[str] = None
    file_path: Optional[str] = None
    description: Optional[str] = None


class PTWeightFileResponse(PTWeightFileBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True