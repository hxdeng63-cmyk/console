# AIoT Device Management Platform — REST API Specification

**Version**: 1.0.0
**Base URL**: `https://api.ai-console.example.com/api/v1`
**Authentication**: Bearer JWT

---

## Conventions

### Authentication
All endpoints except `/auth/login` and `/auth/refresh` require:
```
Authorization: Bearer <access_token>
```

### Pagination
List endpoints support cursor-based pagination:
```
GET /resources?cursor=<cursor>&limit=20
```
Response envelope:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [],
    "next_cursor": "eyJpZCI6MTIzfQ==",
    "has_more": true
  }
}
```

### Error Handling
```json
{
  "code": <error_code>,
  "message": "<error_message>",
  "request_id": "req_abc123"
}
```

For validation errors (422), field-level details are included:
```json
{
  "code": 422,
  "message": "Validation failed",
  "request_id": "req_abc123",
  "errors": [
    { "field": "email", "message": "Invalid email format" },
    { "field": "password", "message": "Must be at least 8 characters" }
  ]
}
```

### Rate Limiting
Rate limit headers are included in all responses:
| Header | Description |
|--------|-------------|
| X-RateLimit-Limit | Maximum requests per window |
| X-RateLimit-Remaining | Remaining requests in current window |
| X-RateLimit-Reset | Unix timestamp when the rate limit resets |

| code | description |
|------|-------------|
| 400 | Bad Request — invalid parameters |
| 401 | Unauthorized — token missing/expired |
| 403 | Forbidden — insufficient permissions |
| 404 | Not Found |
| 409 | Conflict — resource already exists |
| 422 | Validation Error |
| 429 | Rate Limited |
| 500 | Internal Server Error |

### Rate Limit Headers
All API responses include rate limit headers:
- X-RateLimit-Limit: Request limit per window
- X-RateLimit-Remaining: Remaining requests in window
- X-RateLimit-Reset: Unix timestamp when limit resets

### Timestamps
All timestamps are ISO 8601 UTC: `2026-04-23T10:30:00Z`

### Status Field Representation
The API accepts string synonyms that map to SMALLINT values in the database:

| API String | DB Value | Description |
|------------|---------|-------------|
| `active` | 1 | Active/Enabled |
| `disabled` | 0 | Disabled/Inactive |
| `online` | 1 | Device online (online_status only) |
| `offline` | 0 | Device offline (online_status only) |

Example: `status: "active"` in API request is stored as `1` in DB.

### Memory/Disk Size Format
`memory_size` and `disk_size` are stored as bytes (BIGINT) in the database.
API responses return human-readable strings:

| DB Value (bytes) | API Response |
|-----------------|--------------|
| 16777216 | `"16M"` |
| 16384 | `"16K"` |
| 1073741824 | `"1G"` |

The view `v_device_details` provides computed `memory_size_fmt` and `disk_size_fmt` columns.

---

## Endpoints

### 1. Authentication — `/auth`

#### POST /auth/login
```json
// Request
{
  "username": "admin",
  "password": "********",
  "captcha_key": "optional-captcha-token"
}

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 7200,
    "token_type": "Bearer",
    "user": {
      "id": 1,
      "username": "admin",
      "nickname": "Administrator",
      "email": "admin@example.com",
      "roles": ["super_admin"]
    }
  }
}
```

#### POST /auth/refresh
```json
// Request
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 7200
  }
}
```

#### POST /auth/logout
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### GET /auth/me
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "username": "admin",
    "nickname": "Administrator",
    "email": "admin@example.com",
    "phone": "138****8888",
    "roles": ["super_admin"],
    "departments": ["研发部"],
    "last_login_at": "2026-04-23T08:00:00Z",
    "last_login_ip": "192.168.1.100"
  }
}
```

#### PUT /auth/password
```json
// Request
{
  "old_password": "********",
  "new_password": "********"
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### GET /auth/sessions
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "user_id": 1,
        "device_info": "Chrome/Windows",
        "ip": "192.168.1.100",
        "created_at": "2026-04-23T08:00:00Z",
        "expires_at": "2026-04-24T08:00:00Z"
      }
    ]
  }
}
```

#### DELETE /auth/sessions/:id
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### DELETE /auth/sessions
```json
// Response 200
// Revokes all sessions for the current user (except the current one)
{
  "code": 0,
  "message": "success"
}
```

---

### 2. Organization — `/orgs`

#### GET /orgs
```json
// Query: ?cursor=&limit=20&parent_id=0&status=

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "org_name": "总公司",
        "org_code": "HQ",
        "parent_id": 0,
        "sort_order": 0,
        "status": "active",
        "created_at": "2026-01-01T00:00:00Z",
        "children_count": 3
      }
    ],
    "next_cursor": "...",
    "has_more": true
  }
}
```

#### POST /orgs
```json
// Request
{
  "org_name": "研发部",
  "org_code": "RD",
  "parent_id": 1,
  "sort_order": 1,
  "status": "active",
  "remark": "研发中心"
}

// Response 201 Created
{
  "code": 0,
  "message": "success",
  "data": { "id": 5 }
}
```

#### GET /orgs/:id
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 5,
    "org_name": "研发部",
    "org_code": "RD",
    "parent_id": 1,
    "sort_order": 1,
    "status": "active",
    "remark": "研发中心",
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-04-10T14:30:00Z",
    "children": [],
    "users_count": 12
  }
}
```

#### PUT /orgs/:id
```json
// Request
{
  "org_name": "研发部",
  "sort_order": 2,
  "status": "active",
  "remark": "研发中心"
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### PATCH /orgs/:id
```json
// Request
{
  // partial fields to update
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### DELETE /orgs/:id
```json
// Response 200
{
  "code": 0,
  "message": "success"
}

// Response 409 (has children)
{
  "code": 409,
  "message": "组织机构存在子节点，无法删除"
}
```

#### GET /orgs/:id/users
```json
// Query: ?cursor=&limit=20

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [...],
    "next_cursor": "...",
    "has_more": false
  }
}
```

#### GET /orgs/tree
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": 1,
      "org_name": "总公司",
      "org_code": "HQ",
      "children": [
        {
          "id": 5,
          "org_name": "研发部",
          "org_code": "RD",
          "children": []
        }
      ]
    }
  ]
}
```

---

### 3. User — `/users`

#### GET /users
```json
// Query: ?cursor=&limit=20&org_id=&role_id=&status=&keyword=

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "username": "admin",
        "nickname": "Administrator",
        "email": "admin@example.com",
        "phone": "138****8888",
        "org_id": 5,
        "org_name": "研发部",
        "roles": ["super_admin"],
        "status": "active",
        "last_login_at": "2026-04-23T08:00:00Z"
      }
    ],
    "next_cursor": "...",
    "has_more": false
  }
}
```

#### POST /users
```json
// Request
{
  "username": "zhangsan",
  "password": "********",
  "nickname": "张三",
  "email": "zhangsan@example.com",
  "phone": "13900001111",
  "org_id": 5,
  "role_ids": [2, 3],
  "status": "active",
  "remark": "新入职员工"
}

// Response 201 Created
{
  "code": 0,
  "message": "success",
  "data": { "id": 10 }
}
```

#### GET /users/:id
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 10,
    "username": "zhangsan",
    "nickname": "张三",
    "email": "zhangsan@example.com",
    "phone": "13900001111",
    "org_id": 5,
    "org_name": "研发部",
    "roles": [
      { "id": 2, "role_name": "运维人员" },
      { "id": 3, "role_name": "普通用户" }
    ],
    "status": "active",
    "last_login_at": null,
    "created_at": "2026-04-20T10:00:00Z"
  }
}
```

#### PUT /users/:id
```json
// Request
{
  "nickname": "张三（研发）",
  "email": "zhangsan.rd@example.com",
  "phone": "13900001112",
  "org_id": 6,
  "role_ids": [2],
  "status": "active"
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### PATCH /users/:id
```json
// Request
{
  // partial fields to update
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### DELETE /users/:id
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### PUT /users/:id/password
```json
// Request
{
  "password": "********"
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### GET /users/:id/operations
```json
// Query: ?cursor=&limit=20&start_time=&end_time=

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "user_id": 10,
        "username": "zhangsan",
        "action": "更新设备",
        "resource_type": "device",
        "resource_id": 100,
        "resource_name": "边缘视频分析盒_2495eb13",
        "ip": "192.168.1.50",
        "status": "success",
        "created_at": "2026-04-23T10:00:00Z"
      }
    ],
    "next_cursor": "...",
    "has_more": true
  }
}
```

---

### 4. Role — `/roles`

#### GET /roles
```json
// Query: ?cursor=&limit=20&keyword=&status= (cursor and limit are optional)

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "role_name": "超级管理员",
        "role_code": "super_admin",
        "status": "active",
        "is_system": true,
        "user_count": 2,
        "created_at": "2026-01-01T00:00:00Z"
      }
    ],
    "next_cursor": "...",
    "has_more": false
  }
}
```

#### POST /roles
```json
// Request
{
  "role_name": "运维人员",
  "role_code": "operator",
  "status": "active",
  "menu_ids": [1, 2, 3, 4, 5],
  "resource_ids": [101, 102, 103],
  "remark": "负责日常运维工作"
}

// Response 201 Created
{
  "code": 0,
  "message": "success",
  "data": { "id": 5 }
}
```

#### GET /roles/:id
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 5,
    "role_name": "运维人员",
    "role_code": "operator",
    "status": "active",
    "is_system": false,
    "menu_ids": [1, 2, 3, 4, 5],
    "resource_ids": [101, 102, 103],
    "remark": "负责日常运维工作",
    "created_at": "2026-04-01T00:00:00Z",
    "updated_at": "2026-04-15T10:00:00Z",
    "menus": [
      { "id": 1, "menu_name": "设备管理" },
      { "id": 2, "menu_name": "数据源管理" }
    ],
    "resources": [
      { "id": 101, "resource_name": "设备查看" }
    ]
  }
}
```

#### PUT /roles/:id
```json
// Request
{
  "role_name": "运维主管",
  "menu_ids": [1, 2, 3, 4, 5, 6],
  "resource_ids": [101, 102, 103, 104],
  "status": "active"
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### PATCH /roles/:id
```json
// Request
{
  // partial fields to update
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### DELETE /roles/:id
```json
// Response 200
{
  "code": 0,
  "message": "success"
}

// Response 409 (has users)
{
  "code": 409,
  "message": "该角色已分配给用户，无法删除"
}
```

#### GET /roles/:id/users
```json
// Query: ?cursor=&limit=20

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [...],
    "next_cursor": "...",
    "has_more": false
  }
}
```

---

### 5. Menu — `/menus`

#### GET /menus
```json
// Query: ?cursor=&limit=20&status= (cursor and limit are optional)

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "menu_name": "设备管理",
        "menu_code": "device",
        "icon": "Monitor",
        "path": "/layout/device",
        "sort_order": 1,
        "status": "active",
        "children": [
          {
            "id": 11,
            "menu_name": "设备列表",
            "menu_code": "device_list",
            "icon": "List",
            "path": "/layout/device/device",
            "sort_order": 11
          }
        ]
      }
    ],
    "next_cursor": "...",
    "has_more": false
  }
}
```

#### POST /menus
```json
// Request
{
  "menu_name": "算法管理",
  "menu_code": "algorithm",
  "icon": "Cpu",
  "path": "/layout/algorithm",
  "parent_id": 0,
  "sort_order": 5,
  "status": "active"
}

// Response 201 Created
{
  "code": 0,
  "message": "success",
  "data": { "id": 10 }
}
```

#### PUT /menus/:id
```json
// Request
{
  "menu_name": "算法管理",
  "icon": "Box",
  "path": "/layout/algorithm",
  "sort_order": 6,
  "status": "active"
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### DELETE /menus/:id
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

---

### 6. Resource — `/resources`

#### GET /resources
```json
// Query: ?cursor=&limit=20&resource_type= (cursor and limit are optional)

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 101,
        "resource_name": "设备查看",
        "resource_code": "device:view",
        "resource_type": "button",
        "parent_id": null,
        "sort_order": 1
      }
    ],
    "next_cursor": "...",
    "has_more": false
  }
}
```

#### POST /resources
```json
// Request
{
  "resource_name": "设备删除",
  "resource_code": "device:delete",
  "resource_type": "button",
  "parent_id": 101
}

// Response 201 Created
{
  "code": 0,
  "message": "success",
  "data": { "id": 105 }
}
```

#### GET /resources/:id
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 105,
    "resource_name": "设备删除",
    "resource_code": "device:delete",
    "resource_type": "button",
    "parent_id": 101,
    "sort_order": 3,
    "created_at": "2026-04-01T00:00:00Z"
  }
}
```

#### PUT /resources/:id
```json
// Request
{
  "resource_name": "设备删除",
  "resource_code": "device:delete",
  "sort_order": 3
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### PATCH /resources/:id
```json
// Request
{
  // partial fields to update
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### DELETE /resources/:id
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

---

### 7. Device — `/devices`

#### GET /devices
```json
// Query: ?cursor=&limit=20&firmware_version=&department=&online_status=&keyword=

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "device_name": "边缘视频分析盒_2495eb13",
        "device_ip": "192.168.1.100",
        "device_port": 8000,
        "device_sn": "2495eb13-a1b2-c3d4",
        "firmware_version": "v2.1.0",
        "department": "研发部",
        "product_type": "AI Camera",
        "cpu_cores": 8,
        "cpu_usage": 45.5,
        "memory_size": "16G",
        "memory_usage": 62.3,
        "disk_size": "256G",
        "disk_usage": 38.2,
        "video_source_count": 4,
        "online_status": "online",
        "auth_status": "authorized",
        "auth_deadline": "2027-01-01T00:00:00Z",
        "last_heartbeat_at": "2026-04-23T10:00:00Z",
        "created_at": "2026-01-15T10:00:00Z"
      }
    ],
    "next_cursor": "...",
    "has_more": true
  }
}
```

#### POST /devices
```json
// Request
{
  "device_name": "边缘视频分析盒_test001",
  "device_ip": "192.168.1.200",
  "device_port": 8000,
  "device_sn": "test001-a1b2-c3d4",
  "product_type": "AI Box",
  "department": "测试部",
  "group_id": 3
}

// Response 201 Created
{
  "code": 0,
  "message": "success",
  "data": { "id": 100 }
}
```

#### GET /devices/:id
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 100,
    "device_name": "边缘视频分析盒_test001",
    "device_ip": "192.168.1.200",
    "device_port": 8000,
    "device_sn": "test001-a1b2-c3d4",
    "firmware_version": "v2.1.0",
    "department": "测试部",
    "product_type": "AI Box",
    "cpu_cores": 4,
    "cpu_usage": 30.0,
    "memory_size": "8G",
    "memory_usage": 45.0,
    "disk_size": "128G",
    "disk_usage": 20.0,
    "video_source_count": 2,
    "online_status": "online",
    "auth_status": "unauthorized",
    "auth_deadline": null,
    "group_id": 3,
    "group_name": "测试设备组",
    "region_id": 2,
    "region_name": "东区",
    "last_heartbeat_at": "2026-04-23T09:55:00Z",
    "created_at": "2026-04-10T10:00:00Z",
    "updated_at": "2026-04-20T14:30:00Z"
  }
}
```

#### PUT /devices/:id
```json
// Request
{
  "device_name": "边缘视频分析盒_test001_updated",
  "department": "生产部",
  "group_id": 4
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### PATCH /devices/:id
```json
// Request
{
  // partial fields to update
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### DELETE /devices/:id
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### POST /devices/batch-delete
```json
// Request
{
  "device_ids": [1, 2, 3]
}

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "deleted_count": 3
  }
}
```

#### PUT /devices/batch-update
```json
// Request
{
  "device_ids": [1, 2, 3],
  "department": "生产部"
}

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "updated_count": 3
  }
}
```

#### DELETE /devices/:id/auth
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### GET /devices/:id/stats
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "device_id": 1,
    "cpu_usage": 45.5,
    "memory_usage": 62.3,
    "disk_usage": 38.2,
    "video_sources": 4,
    "online_status": "online",
    "last_heartbeat_at": "2026-04-23T10:00:00Z",
    "uptime_seconds": 864000
  }
}
```

#### POST /devices/:id/auth
```json
// Request
{
  "auth_code": "ABCD-1234-EFGH-5678",
  "auth_deadline": "2027-01-01T00:00:00Z"
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### GET /devices/:id/video-sources
```json
// Query: ?cursor=&limit=20&status=

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "device_id": 1,
        "channel_id": 1,
        "channel_name": "主摄像头",
        "stream_url": "rtsp://192.168.1.100:554/stream1",
        "status": "active",
        "resolution": "1920x1080",
        "fps": 25,
        "bitrate": 4096
      }
    ],
    "next_cursor": "...",
    "has_more": false
  }
}
```

#### GET /devices/export
```json
// Query: ?format=xlsx&firmware_version=&department=&online_status=

// Response 200 (binary stream)
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
```

---

### 8. Device Group — `/device-groups`

#### GET /device-groups
```json
// Query: ?cursor=&limit=20&region_id=&keyword=

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "group_name": "研发部设备组",
        "group_code": "RD_GROUP",
        "region_id": 1,
        "region_name": "北区",
        "parent_id": 0,
        "device_count": 15,
        "online_count": 12,
        "created_at": "2026-01-15T10:00:00Z"
      }
    ],
    "next_cursor": "...",
    "has_more": false
  }
}
```

#### POST /device-groups
```json
// Request
{
  "group_name": "测试设备组",
  "group_code": "TEST_GROUP",
  "region_id": 2,
  "parent_id": 0,
  "sort_order": 1
}

// Response 201 Created
{
  "code": 0,
  "message": "success",
  "data": { "id": 10 }
}
```

#### GET /device-groups/:id
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 10,
    "group_name": "测试设备组",
    "group_code": "TEST_GROUP",
    "region_id": 2,
    "region_name": "东区",
    "parent_id": 0,
    "device_count": 8,
    "online_count": 6,
    "created_at": "2026-04-01T00:00:00Z",
    "children": [],
    "devices": []
  }
}
```

#### PUT /device-groups/:id
```json
// Request
{
  "group_name": "测试设备组（新）",
  "region_id": 3,
  "sort_order": 2
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### PATCH /device-groups/:id
```json
// Request
{
  // partial fields to update
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### DELETE /device-groups/:id
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### GET /device-groups/:id/devices
```json
// Query: ?cursor=&limit=20

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [...],
    "next_cursor": "...",
    "has_more": false
  }
}
```

#### POST /device-groups/:id/devices
```json
// Request
{
  "device_ids": [1, 2, 3]
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### DELETE /device-groups/:id/devices
```json
// Request
{
  "device_ids": [1, 2]
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### GET /device-groups/tree
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": [...]
}
```

---

### 9. Region — `/regions`

#### GET /regions
```json
// Query: ?cursor=&limit=20&status= (cursor and limit are optional)

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "region_name": "北区",
        "region_code": "NORTH",
        "parent_id": 0,
        "sort_order": 1,
        "device_count": 50
      }
    ],
    "next_cursor": "...",
    "has_more": false
  }
}
```

#### POST /regions
```json
// Request
{
  "region_name": "东区",
  "region_code": "EAST",
  "parent_id": 0,
  "sort_order": 2
}

// Response 201 Created
{
  "code": 0,
  "message": "success",
  "data": { "id": 5 }
}
```

#### GET /regions/:id
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 5,
    "region_name": "东区",
    "region_code": "EAST",
    "parent_id": 0,
    "sort_order": 2,
    "device_count": 35,
    "children": []
  }
}
```

#### PUT /regions/:id
```json
// Request
{
  "region_name": "东区",
  "sort_order": 3
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### PATCH /regions/:id
```json
// Request
{
  // partial fields to update
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### DELETE /regions/:id
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### GET /regions/tree
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": [...]
}
```

---

### 10. Data Source — `/data-sources`

#### GET /data-sources
```json
// Query: ?cursor=&limit=20&device_id=&type=&status=

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "source_name": "主摄像头_01",
        "source_type": "rtsp",
        "device_id": 1,
        "device_name": "边缘视频分析盒_2495eb13",
        "stream_url": "rtsp://192.168.1.100:554/stream1",
        "status": "active",
        "channel_no": 1,
        "resolution": "1920x1080",
        "created_at": "2026-01-20T10:00:00Z"
      }
    ],
    "next_cursor": "...",
    "has_more": true
  }
}
```

#### POST /data-sources
```json
// Request
{
  "source_name": "主摄像头_02",
  "source_type": "rtsp",
  "device_id": 1,
  "stream_url": "rtsp://192.168.1.100:554/stream2",
  "channel_no": 2,
  "resolution": "1280x720"
}

// Response 201 Created
{
  "code": 0,
  "message": "success",
  "data": { "id": 10 }
}
```

#### GET /data-sources/:id
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 10,
    "source_name": "主摄像头_02",
    "source_type": "rtsp",
    "device_id": 1,
    "device_name": "边缘视频分析盒_2495eb13",
    "stream_url": "rtsp://192.168.1.100:554/stream2",
    "status": "active",
    "channel_no": 2,
    "resolution": "1280x720",
    "created_at": "2026-04-15T10:00:00Z"
  }
}
```

#### PUT /data-sources/:id
```json
// Request
{
  "source_name": "主摄像头_02（已修改）",
  "stream_url": "rtsp://192.168.1.100:554/stream2_new"
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### PATCH /data-sources/:id
```json
// Request
{
  // partial fields to update
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### DELETE /data-sources/:id
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### POST /data-sources/:id/test
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "connectable": true,
    "delay_ms": 85,
    "resolution": "1920x1080"
  }
}
```

---

### 11. Platform Access — `/platforms`

#### GET /platforms
```json
// Query: ?cursor=&limit=20&platform_type= (cursor and limit are optional)

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "platform_name": "GB28181",
        "platform_type": "gb28181",
        "server_ip": "192.168.10.100",
        "server_port": 5060,
        "device_count": 50,
        "status": "active",
        "created_at": "2026-01-10T00:00:00Z"
      }
    ],
    "next_cursor": "...",
    "has_more": false
  }
}
```

#### POST /platforms
```json
// Request
{
  "platform_name": "ONVIF设备",
  "platform_type": "onvif",
  "server_ip": "192.168.10.200",
  "server_port": 80,
  "username": "admin",
  "password": "********"
}

// Response 201 Created
{
  "code": 0,
  "message": "success",
  "data": { "id": 5 }
}
```

#### GET /platforms/:id
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 5,
    "platform_name": "ONVIF设备",
    "platform_type": "onvif",
    "server_ip": "192.168.10.200",
    "server_port": 80,
    "device_count": 25,
    "status": "active",
    "created_at": "2026-04-01T00:00:00Z"
  }
}
```

#### PUT /platforms/:id
```json
// Request
{
  "platform_name": "ONVIF设备（修改）",
  "server_ip": "192.168.10.201"
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### PATCH /platforms/:id
```json
// Request
{
  // partial fields to update
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### DELETE /platforms/:id
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### POST /platforms/:id/sync
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "task_id": "sync_123456",
    "status": "running",
    "device_count": 25
  }
}
```

#### GET /platforms/:id/sync-status
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "task_id": "sync_123456",
    "status": "completed",
    "total_count": 25,
    "success_count": 24,
    "fail_count": 1,
    "fail_devices": [
      { "device_sn": "xxx", "reason": "认证失败" }
    ],
    "started_at": "2026-04-23T10:00:00Z",
    "completed_at": "2026-04-23T10:05:00Z"
  }
}
```

---

### 12. Algorithm — `/algorithms`

#### GET /algorithms
```json
// Query: ?cursor=&limit=20&type=&status=

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "algorithm_name": "人脸检测",
        "algorithm_type": "face_detection",
        "algorithm_code": "face_det_v1",
        "version": "1.0.0",
        "provider": "internal",
        "model_path": "/models/face_det_v1.onnx",
        "config": {
          "confidence_threshold": 0.5,
          "nms_threshold": 0.4
        },
        "status": "active",
        "device_count": 10,
        "created_at": "2026-01-15T00:00:00Z"
      }
    ],
    "next_cursor": "...",
    "has_more": true
  }
}
```

#### POST /algorithms
```json
// Request
{
  "algorithm_name": "目标检测",
  "algorithm_type": "object_detection",
  "algorithm_code": "obj_det_v1",
  "version": "1.0.0",
  "provider": "internal",
  "model_path": "/models/obj_det_v1.onnx",
  "config": {
    "confidence_threshold": 0.6,
    "class_names": ["person", "car", "bicycle"]
  }
}

// Response 201 Created
{
  "code": 0,
  "message": "success",
  "data": { "id": 10 }
}
```

#### GET /algorithms/:id
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 10,
    "algorithm_name": "目标检测",
    "algorithm_type": "object_detection",
    "algorithm_code": "obj_det_v1",
    "version": "1.0.0",
    "provider": "internal",
    "model_path": "/models/obj_det_v1.onnx",
    "config": {
      "confidence_threshold": 0.6,
      "class_names": ["person", "car", "bicycle"]
    },
    "status": "active",
    "device_count": 5,
    "created_at": "2026-04-10T00:00:00Z"
  }
}
```

#### PUT /algorithms/:id
```json
// Request
{
  "algorithm_name": "目标检测（优化版）",
  "config": {
    "confidence_threshold": 0.7,
    "class_names": ["person", "car", "bicycle", "motorcycle"]
  }
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### PATCH /algorithms/:id
```json
// Request
{
  // partial fields to update
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### DELETE /algorithms/:id
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### POST /algorithms/:id/deploy
```json
// Request
{
  "device_ids": [1, 2, 3]
}

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "deployment_id": 100,
    "device_count": 3
  }
}
```

---

### 13. Algorithm Service — `/algorithm-services`

#### GET /algorithm-services
```json
// Query: ?cursor=&limit=20&device_id=&algorithm_id=&status=

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "service_name": "人脸检测服务_01",
        "algorithm_id": 1,
        "algorithm_name": "人脸检测",
        "device_id": 1,
        "device_name": "边缘视频分析盒_2495eb13",
        "status": "running",
        "channel_configs": [
          { "channel_id": 1, "enabled": true, "config": {} },
          { "channel_id": 2, "enabled": false, "config": {} }
        ],
        "created_at": "2026-02-01T10:00:00Z"
      }
    ],
    "next_cursor": "...",
    "has_more": true
  }
}
```

#### POST /algorithm-services
```json
// Request
{
  "service_name": "目标检测服务_01",
  "algorithm_id": 2,
  "device_id": 1,
  "channel_configs": [
    { "channel_id": 1, "enabled": true, "config": { "roi": "0,0,1920,1080" } }
  ]
}

// Response 201 Created
{
  "code": 0,
  "message": "success",
  "data": { "id": 10 }
}
```

#### GET /algorithm-services/:id
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 10,
    "service_name": "目标检测服务_01",
    "algorithm_id": 2,
    "algorithm_name": "目标检测",
    "device_id": 1,
    "device_name": "边缘视频分析盒_2495eb13",
    "status": "running",
    "channel_configs": [...],
    "created_at": "2026-04-15T10:00:00Z"
  }
}
```

#### PUT /algorithm-services/:id
```json
// Request
{
  "service_name": "目标检测服务_01（修改）",
  "channel_configs": [
    { "channel_id": 1, "enabled": true, "config": { "roi": "0,0,1920,800" } },
    { "channel_id": 2, "enabled": true, "config": { "roi": "0,0,1920,1080" } }
  ]
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### PATCH /algorithm-services/:id
```json
// Request
{
  // partial fields to update
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### DELETE /algorithm-services/:id
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### POST /algorithm-services/:id/start
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### POST /algorithm-services/:id/stop
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### GET /algorithm-services/:id/stats
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "service_id": 10,
    "status": "running",
    "start_time": "2026-04-23T08:00:00Z",
    "uptime_seconds": 7200,
    "total_events": 1520,
    "events_today": 120,
    "cpu_usage": 25.5,
    "memory_usage": 512
  }
}
```

---

### 14. Algorithm Event — `/algorithm-events`

#### GET /algorithm-events
```json
// Query: ?cursor=&limit=20&device_id=&algorithm_id=&event_type=&start_time=&end_time=

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "device_id": 1,
        "device_name": "边缘视频分析盒_2495eb13",
        "algorithm_id": 1,
        "algorithm_name": "人脸检测",
        "event_type": "face_detected",
        "event_data": {
          "face_count": 2,
          "confidence": 0.95,
          "image_url": "/storage/events/face_001.jpg"
        },
        "source_channel": 1,
        "occurred_at": "2026-04-23T10:30:00Z"
      }
    ],
    "next_cursor": "eyJpZCI6MX0=",
    "has_more": true
  }
}
```

#### GET /algorithm-events/:id
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "device_id": 1,
    "device_name": "边缘视频分析盒_2495eb13",
    "algorithm_id": 1,
    "algorithm_name": "人脸检测",
    "event_type": "face_detected",
    "event_data": {
      "face_count": 2,
      "confidence": 0.95,
      "image_url": "/storage/events/face_001.jpg"
    },
    "source_channel": 1,
    "occurred_at": "2026-04-23T10:30:00Z",
    "handled": false
  }
}
```

#### PUT /algorithm-events/:id/handle
```json
// Request
{
  "handled": true,
  "remark": "已确认，为内部员工"
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### POST /algorithm-events/batch-handle
```json
// Request
{
  "event_ids": [1, 2, 3],
  "handled": true,
  "remark": "批量确认为正常事件"
}

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "updated_count": 3
  }
}
```

#### GET /algorithm-events/stats
```json
// Query: ?start_time=2026-04-01&end_time=2026-04-23&group_by=algorithm

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "total_count": 15230,
    "today_count": 120,
    "by_algorithm": [
      {
        "algorithm_id": 1,
        "algorithm_name": "人脸检测",
        "count": 8500
      },
      {
        "algorithm_id": 2,
        "algorithm_name": "目标检测",
        "count": 6730
      }
    ],
    "by_device": [...],
    "by_hour": [...]
  }
}
```

---

### 15. Linkage Rule — `/linkage-rules`

#### GET /linkage-rules
```json
// Query: ?cursor=&limit=20&status=&trigger_type=

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "rule_name": "人脸检测联动告警",
        "rule_code": "FACE_ALERT_01",
        "trigger_type": "algorithm_event",
        "trigger_config": {
          "algorithm_id": 1,
          "event_type": "face_detected",
          "condition": "face_count > 0"
        },
        "action_type": "notify",
        "action_config": {
          "notification_types": ["email", "sms"],
          "recipients": ["13800001111"]
        },
        "status": "active",
        "trigger_count": 1520,
        "last_trigger_at": "2026-04-23T10:30:00Z",
        "created_at": "2026-02-01T00:00:00Z"
      }
    ],
    "next_cursor": "...",
    "has_more": false
  }
}
```

#### POST /linkage-rules
```json
// Request
{
  "rule_name": "区域入侵联动",
  "rule_code": "INTRUSION_ALERT_01",
  "trigger_type": "algorithm_event",
  "trigger_config": {
    "algorithm_id": 3,
    "event_type": "intrusion_detected",
    "condition": "confidence > 0.8"
  },
  "action_type": "linkage",
  "action_config": {
    "device_ids": [1, 2],
    "actions": [
      { "type": "start_recording", "duration": 60 },
      { "type": "send_alert", "channels": ["email"] }
    ]
  },
  "status": "active"
}

// Response 201 Created
{
  "code": 0,
  "message": "success",
  "data": { "id": 10 }
}
```

#### GET /linkage-rules/:id
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 10,
    "rule_name": "区域入侵联动",
    "rule_code": "INTRUSION_ALERT_01",
    "trigger_type": "algorithm_event",
    "trigger_config": {...},
    "action_type": "linkage",
    "action_config": {...},
    "status": "active",
    "trigger_count": 85,
    "last_trigger_at": "2026-04-22T15:00:00Z",
    "created_at": "2026-04-01T00:00:00Z"
  }
}
```

#### PUT /linkage-rules/:id
```json
// Request
{
  "rule_name": "区域入侵联动（优化）",
  "trigger_config": {
    "algorithm_id": 3,
    "event_type": "intrusion_detected",
    "condition": "confidence > 0.85"
  },
  "status": "active"
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### PATCH /linkage-rules/:id
```json
// Request
{
  // partial fields to update
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### DELETE /linkage-rules/:id
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### POST /linkage-rules/:id/test
```json
// Request
{
  "test_data": {
    "algorithm_id": 3,
    "event_type": "intrusion_detected",
    "confidence": 0.9
  }
}

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "triggered": true,
    "actions_executed": [
      { "type": "start_recording", "success": true },
      { "type": "send_alert", "success": true }
    ]
  }
}
```

---

### 16. Linkage History — `/linkage-histories`

#### GET /linkage-histories
```json
// Query: ?cursor=&limit=20&rule_id=&trigger_type=&start_time=&end_time=

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "rule_id": 10,
        "rule_name": "区域入侵联动",
        "trigger_type": "algorithm_event",
        "trigger_source": {
          "device_id": 1,
          "device_name": "边缘视频分析盒_2495eb13",
          "event_id": 5001,
          "event_data": {...}
        },
        "action_results": [
          { "type": "start_recording", "success": true },
          { "type": "send_alert", "success": true }
        ],
        "status": "success",
        "triggered_at": "2026-04-23T10:30:00Z"
      }
    ],
    "next_cursor": "eyJpZCI6MX0=",
    "has_more": true
  }
}
```

#### GET /linkage-histories/:id
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "rule_id": 10,
    "rule_name": "区域入侵联动",
    "trigger_type": "algorithm_event",
    "trigger_source": {...},
    "action_results": [...],
    "status": "success",
    "triggered_at": "2026-04-23T10:30:00Z",
    "completed_at": "2026-04-23T10:30:02Z"
  }
}
```

---

### 17. Notification — `/notifications`

#### GET /notifications
```json
// Query: ?cursor=&limit=20&type=&is_read=

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "type": "system",
        "title": "系统更新通知",
        "content": "系统将于今晚23:00进行版本更新",
        "is_read": false,
        "created_at": "2026-04-23T09:00:00Z"
      }
    ],
    "next_cursor": "...",
    "has_more": true,
    "unread_count": 5
  }
}
```

#### PUT /notifications/:id/read
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### PUT /notifications/read-all
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": { "updated_count": 5 }
}
```

#### DELETE /notifications/:id
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

---

### 18. License — `/licenses`

#### GET /licenses
```json
// Query: ?cursor=&limit=20&status= (cursor and limit are optional)

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "license_key": "LIC-XXXX-XXXX-XXXX",
        "license_type": "enterprise",
        "max_devices": 1000,
        "max_users": 100,
        "expire_at": "2027-01-01T00:00:00Z",
        "status": "active",
        "created_at": "2026-01-01T00:00:00Z"
      }
    ],
    "next_cursor": "...",
    "has_more": false
  }
}
```

#### POST /licenses
```json
// Request
{
  "license_key": "LIC-XXXX-XXXX-XXXX",
  "max_devices": 1000,
  "max_users": 100,
  "expire_at": "2027-01-01T00:00:00Z"
}

// Response 201 Created
{
  "code": 0,
  "message": "success",
  "data": { "id": 2 }
}
```

#### GET /licenses/verify
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "valid": true,
    "license_type": "enterprise",
    "max_devices": 1000,
    "max_users": 100,
    "expire_at": "2027-01-01T00:00:00Z",
    "days_remaining": 253
  }
}
```

#### DELETE /licenses/:id
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

---

### 19. Firmware — `/firmwares`

#### GET /firmwares
```json
// Query: ?cursor=&limit=20&product_type=

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "version": "v2.1.0",
        "product_type": "AI Camera",
        "file_path": "/firmware/v2.1.0_ai_camera.bin",
        "file_size": 52428800,
        "md5": "d41d8cd98f00b204e9800998ecf8427e",
        "release_note": "优化了人脸检测算法",
        "is_latest": true,
        "status": "active",
        "created_at": "2026-03-15T00:00:00Z"
      }
    ],
    "next_cursor": "...",
    "has_more": false
  }
}
```

#### POST /firmwares
```json
// Request (multipart/form-data)
{
  "version": "v2.1.1",
  "product_type": "AI Camera",
  "file": <binary>,
  "release_note": "修复了若干bug",
  "is_latest": true
}

// Response 201 Created
{
  "code": 0,
  "message": "success",
  "data": { "id": 5 }
}
```

#### GET /firmwares/:id
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 5,
    "version": "v2.1.1",
    "product_type": "AI Camera",
    "file_path": "/firmware/v2.1.1_ai_camera.bin",
    "file_size": 52428800,
    "md5": "...",
    "release_note": "修复了若干bug",
    "is_latest": true,
    "status": "active",
    "created_at": "2026-04-20T00:00:00Z"
  }
}
```

#### PUT /firmwares/:id
```json
// Request
{
  "release_note": "修复了已知问题",
  "is_latest": true
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### PATCH /firmwares/:id
```json
// Request
{
  // partial fields to update
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### DELETE /firmwares/:id
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### POST /firmwares/:id/upgrade
```json
// Request
{
  "device_ids": [1, 2, 3]
}

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "upgrade_task_id": "upg_123456",
    "device_count": 3
  }
}
```

---

### 20. System Setting — `/system-settings`

#### GET /system-settings
```json
// Query: ?group=notification

// Response 200
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": 1,
      "setting_key": "notification.email.enabled",
      "setting_value": "true",
      "setting_type": "boolean",
      "group": "notification",
      "remark": "邮件通知开关"
    }
  ]
}
```

#### PUT /system-settings
```json
// Request
{
  "settings": [
    {
      "setting_key": "notification.email.enabled",
      "setting_value": "true"
    },
    {
      "setting_key": "notification.sms.enabled",
      "setting_value": "false"
    }
  ]
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### GET /system-settings/:key
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "setting_key": "notification.email.enabled",
    "setting_value": "true",
    "setting_type": "boolean"
  }
}
```

#### PUT /system-settings/:key
```json
// Request
{ "setting_value": "false" }

// Response 200
{
  "code": 0,
  "message": "success"
}
```

---

### 21. Operation Log — `/operation-logs`

#### GET /operation-logs
```json
// Query: ?cursor=&limit=20&user_id=&action=&resource_type=&start_time=&end_time=

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "user_id": 1,
        "username": "admin",
        "action": "更新设备",
        "resource_type": "device",
        "resource_id": 1,
        "resource_name": "边缘视频分析盒_2495eb13",
        "ip": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "request_body": {},
        "response_status": 200,
        "created_at": "2026-04-23T10:00:00Z"
      }
    ],
    "next_cursor": "eyJpZCI6MX0=",
    "has_more": true
  }
}
```

#### GET /operation-logs/export
```json
// Query: ?format=xlsx&start_time=2026-04-01&end_time=2026-04-23

// Response 200 (binary stream)
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
```

---

### 22. File Manager — `/files`

#### GET /files
```json
// Query: ?cursor=&limit=20&category=image&keyword=

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "file_name": "event_20260423_001.jpg",
        "file_path": "/storage/events/event_20260423_001.jpg",
        "file_size": 102400,
        "mime_type": "image/jpeg",
        "category": "event",
        "created_at": "2026-04-23T10:30:00Z"
      }
    ],
    "next_cursor": "...",
    "has_more": true
  }
}
```

#### POST /files
```json
// Request (multipart/form-data)
{
  "file": <binary>,
  "category": "event",
  "remark": "事件截图"
}

// Response 201 Created
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 10,
    "file_name": "event_20260423_010.jpg",
    "file_path": "/storage/events/event_20260423_010.jpg",
    "file_size": 102400
  }
}
```

#### DELETE /files/:id
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### GET /files/:id/download
```json
// Response 200 (binary stream)
Content-Type: image/jpeg
```

---

### 23. Help Center — `/help`

#### GET /help/articles
```json
// Query: ?cursor=&limit=20&category=usage&keyword=

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "如何添加设备",
        "category": "usage",
        "content": "...",
        "views": 1520,
        "created_at": "2026-01-15T00:00:00Z"
      }
    ],
    "next_cursor": "...",
    "has_more": false
  }
}
```

#### GET /help/articles/:id
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "title": "如何添加设备",
    "category": "usage",
    "content": "...",
    "views": 1521,
    "updated_at": "2026-04-20T10:00:00Z"
  }
}
```

---

### 24. Upgrade — `/upgrade`

#### GET /upgrade/check
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "current_version": "v1.5.0",
    "latest_version": "v1.6.0",
    "has_update": true,
    "release_note": "新功能：支持更多算法类型",
    "force_update": false
  }
}
```

#### POST /upgrade/download
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "task_id": "dl_123456",
    "status": "downloading",
    "progress": 0
  }
}
```

#### GET /upgrade/download-status
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "task_id": "dl_123456",
    "status": "completed",
    "file_path": "/upgrade/v1.6.0.zip",
    "file_size": 104857600
  }
}
```

#### POST /upgrade/execute
```json
// Request
{
  "backup": true
}

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "task_id": "upg_789012",
    "status": "upgrading",
    "estimated_time": 300
  }
}
```

#### GET /upgrade/upgrade-status
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "task_id": "upg_789012",
    "status": "completed",
    "previous_version": "v1.5.0",
    "current_version": "v1.6.0",
    "completed_at": "2026-04-23T11:00:00Z"
  }
}
```

---

## Appendix

### Permission Code Reference

| Code | Description |
|------|-------------|
| `system:user:view` | 查看用户列表 |
| `system:user:create` | 创建用户 |
| `system:user:update` | 更新用户 |
| `system:user:delete` | 删除用户 |
| `system:role:view` | 查看角色 |
| `system:role:manage` | 管理角色 |
| `system:menu:view` | 查看菜单 |
| `system:menu:manage` | 管理菜单 |
| `system:resource:view` | 查看资源 |
| `system:resource:manage` | 管理资源 |
| `system:org:view` | 查看组织 |
| `system:org:manage` | 管理组织 |
| `device:view` | 查看设备 |
| `device:create` | 创建设备 |
| `device:update` | 更新设备 |
| `device:delete` | 删除设备 |
| `device:auth` | 设备授权 |
| `device:export` | 导出设备 |
| `datasource:view` | 查看数据源 |
| `datasource:manage` | 管理数据源 |
| `algorithm:view` | 查看算法 |
| `algorithm:manage` | 管理算法 |
| `linkage:view` | 查看联动规则 |
| `linkage:manage` | 管理联动规则 |
| `license:view` | 查看许可证 |
| `license:manage` | 管理许可证 |
| `log:view` | 查看操作日志 |
| `log:export` | 导出日志 |

### Status Value Reference

| Entity | Status Values |
|--------|---------------|
| User | `active`, `disabled` |
| Role | `active`, `disabled` |
| Organization | `active`, `disabled` |
| Menu | `active`, `disabled` |
| Device | `online`, `offline` |
| Device Auth | `authorized`, `unauthorized`, `expired` |
| Data Source | `active`, `inactive` |
| Algorithm | `active`, `inactive` |
| Algorithm Service | `running`, `stopped`, `error` |
| Linkage Rule | `active`, `disabled` |
| Linkage History | `success`, `failed` |
| Notification | `read`, `unread` |
| License | `active`, `expired`, `revoked` |
| Firmware | `active`, `deprecated` |

### Device Online Status Values

| Status | Description |
|--------|-------------|
| `online` | 设备在线 |
| `offline` | 设备离线 |

### Algorithm Event Type Values

| Type | Description |
|------|-------------|
| `face_detected` | 检测到人脸 |
| `face_disappeared` | 人脸消失 |
| `intrusion_detected` | 区域入侵 |
| `object_detected` | 目标检测 |
| `crowd_gathering` | 人群聚集 |
| `vehicle_detected` | 车辆检测 |

### 25. Deployment — `/deployments`

#### GET /deployments
```json
// Query: ?cursor=&limit=20&status=&type=

// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "算法部署任务1",
        "type": "algorithm",
        "target_ids": [1, 2, 3],
        "config": {},
        "status": 1,
        "progress": 75,
        "total_targets": 4,
        "succeeded": 3,
        "failed": 0,
        "created_at": "2026-04-23T08:00:00Z",
        "updated_at": "2026-04-23T10:30:00Z"
      }
    ],
    "next_cursor": "...",
    "has_more": true
  }
}
```

#### POST /deployments
```json
// Request
{
  "name": "算法部署任务1",
  "type": "algorithm",
  "target_ids": [1, 2, 3],
  "config": {}
}

// Response 201 Created
{
  "code": 0,
  "message": "success",
  "data": { "id": 1 }
}
```

#### GET /deployments/:id
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "name": "算法部署任务1",
    "type": "algorithm",
    "target_ids": [1, 2, 3],
    "config": {},
    "status": 1,
    "progress": 75,
    "total_targets": 4,
    "succeeded": 3,
    "failed": 0,
    "created_at": "2026-04-23T08:00:00Z",
    "updated_at": "2026-04-23T10:30:00Z"
  }
}
```

#### PUT /deployments/:id
```json
// Request
{
  "name": "算法部署任务1（已更新）",
  "config": {}
}

// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### DELETE /deployments/:id
```json
// Response 200
{
  "code": 0,
  "message": "success"
}
```

#### GET /deployments/:id/annotations
```json
// Response 200
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "deployment_id": 1,
        "device_id": 1,
        "type": "area",
        "polygon": {},
        "note": "标注信息",
        "created_at": "2026-04-23T09:00:00Z"
      }
    ]
  }
}
```

#### POST /deployments/:id/annotations
```json
// Request
{
  "device_id": 1,
  "type": "area",
  "polygon": {},
  "note": "标注信息"
}

// Response 201 Created
{
  "code": 0,
  "message": "success",
  "data": { "id": 1 }
}
```
