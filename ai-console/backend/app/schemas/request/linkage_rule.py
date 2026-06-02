from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional, Any


class LinkageRuleRequest(BaseModel):
    rule_name: str
    trigger_mode: str = "AUTO"
    algorithm_id: Optional[int] = None
    event_type_id: Optional[int] = None
    level: int = 1
    delay_push: int = 0
    is_compliant: Optional[str] = None
    unit: Optional[str] = None
    action_type: Optional[str] = None
    status: str = "active"
    link: Optional[str] = None
    content: Optional[str] = None
    importance_level: int = 1
    send_frequency: Optional[str] = None
    push_channels: Optional[Any] = None
    selected_devices: Optional[list[int]] = None
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    template_id: Optional[str] = None
    push_target: Optional[str] = None
    remark: Optional[str] = None


class LinkageRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rule_name: str
    trigger_mode: str
    algorithm_id: Optional[int]
    event_type_id: Optional[int]
    level: int
    delay_push: int
    is_compliant: Optional[str]
    unit: Optional[str]
    action_type: Optional[str]
    status: str
    link: Optional[str]
    content: Optional[str]
    importance_level: int
    send_frequency: Optional[str]
    push_channels: Optional[Any]
    app_id: Optional[str]
    app_secret: Optional[str]
    template_id: Optional[str]
    push_target: Optional[str]
    remark: Optional[str]
    selected_devices: Optional[list[int]] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class DeploymentScheduleRequest(BaseModel):
    deployment_id: int
    day_of_week: int
    start_time: str
    end_time: str


class DeploymentScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    deployment_id: int
    day_of_week: int
    start_time: str
    end_time: str
    status: Optional[str] = "active"
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    @classmethod
    def model_validate(cls, item):
        data = item.__dict__.copy()
        # Convert time objects to strings
        if data.get('start_time'):
            data['start_time'] = str(data['start_time'])
        if data.get('end_time'):
            data['end_time'] = str(data['end_time'])
        return super().model_validate(data)