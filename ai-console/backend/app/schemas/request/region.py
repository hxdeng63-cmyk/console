from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class RegionRequest(BaseModel):
    name: str
    code: Optional[str] = None
    parent_id: Optional[int] = None
    level: int = 1
    sort: int = 0


class RegionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: Optional[str]
    parent_id: Optional[int]
    level: int
    sort: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class RegionTreeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: Optional[str]
    parent_id: Optional[int]
    level: int
    sort: int
    children: list["RegionTreeResponse"] = []