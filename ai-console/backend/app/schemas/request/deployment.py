from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class DeploymentRequest(BaseModel):
    name: Optional[str] = None
    algorithm_id: Optional[int] = None
    service_id: Optional[int] = None
    status: str = "active"
    algorithm_status: str = "running"
    device_ids: list[int] = []
    schedule: Optional[dict] = None


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