from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional


class UserRegisterRequest(BaseModel):
    username: str
    password: str
    real_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    org_id: Optional[int] = None


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserRequest(BaseModel):
    username: str
    real_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    org_id: Optional[int] = None
    status: str = "active"
    password: Optional[str] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    real_name: Optional[str]
    avatar: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    gender: Optional[str]
    org_id: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RoleRequest(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    status: str = "active"


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: Optional[str]
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class OrganizationRequest(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    level: int = 1
    sort: int = 0
    code: Optional[str] = None
    remark: Optional[str] = None
    # Frontend-compatible fields
    label: Optional[str] = None
    sortOrder: Optional[int] = None
    parentId: Optional[int] = None
    enabled: bool = True


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent_id: Optional[int]
    level: int
    sort: int
    code: Optional[str]
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class OrganizationTreeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent_id: Optional[int]
    level: int
    sort: int
    code: Optional[str]
    remark: Optional[str]
    children: list["OrganizationTreeResponse"] = []
    # Frontend-compatible aliases
    label: str = ""
    sortOrder: int = 0
    enabled: bool = True


class MenuRequest(BaseModel):
    name: str
    path: Optional[str] = None
    hidden: bool = False
    parent_id: Optional[int] = None
    sort: int = 0
    component: Optional[str] = None
    title: Optional[str] = None
    icon: Optional[str] = None


class MenuResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    path: Optional[str]
    hidden: bool
    parent_id: Optional[int]
    sort: int
    component: Optional[str]
    title: Optional[str]
    icon: Optional[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class MenuTreeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    path: Optional[str]
    hidden: bool
    parent_id: Optional[int]
    sort: int
    component: Optional[str]
    title: Optional[str]
    icon: Optional[str]
    children: list["MenuTreeResponse"] = []


class ResourceRequest(BaseModel):
    resource: str
    resource_group: str
    method: str = "GET"
    service_code: Optional[str] = None
    description: Optional[str] = None
    hidden: bool = False


class ResourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resource: str
    resource_group: str
    method: str
    service_code: Optional[str]
    description: Optional[str]
    hidden: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]