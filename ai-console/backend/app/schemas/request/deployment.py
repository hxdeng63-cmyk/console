from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict


class DeploymentRequest(BaseModel):
    name: Optional[str] = None
    algorithm_id: Optional[int] = None
    service_id: Optional[int] = None
    status: str = "active"
    algorithm_status: str = "running"
    device_ids: list[int] = []
    schedule: Optional[dict] = None

    # Runtime fields (optional on creation, populated by process lifecycle)
    pid: Optional[int] = None
    config_json: Optional[dict] = None
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    exit_code: Optional[int] = None
    log_path: Optional[str] = None
    module_name: Optional[str] = None
    org_id: Optional[int] = None
    region_id: Optional[int] = None


class DeploymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    algorithm_id: Optional[int] = None
    service_id: Optional[int] = None
    status: str
    algorithm_status: str
    deployed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    device_ids: list[int] = []
    schedule: Optional[dict] = None

    # Runtime fields (deployment_token intentionally excluded)
    pid: Optional[int] = None
    config_json: Optional[dict] = None
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    exit_code: Optional[int] = None
    log_path: Optional[str] = None
    module_name: Optional[str] = None
    org_id: Optional[int] = None
    region_id: Optional[int] = None


class DeploymentStartRequest(BaseModel):
    module_name: str
    video_path: str = Field(
        ...,
        description="视频源路径：本地绝对路径，或 rtsp:// / rtmp:// / http:// / https:// 流地址",
    )
    # device_id -> stream_id mapping; required when deployment targets multiple devices
    stream_map: Optional[Dict[int, str]] = None
    # Module-specific configuration merged into the temporary YAML passed to traffic
    config: Optional[dict] = None
    log_path: Optional[str] = None


class DeploymentStartResponse(BaseModel):
    deployment: DeploymentResponse
    deployment_token: str