# API Verification Report

**Date**: 2026-05-25
**Backend**: http://localhost:8080

## Summary

| API | Status | Records | Notes |
|-----|--------|---------|-------|
| `/api/v1/devices` | 200 | 20 | Working |
| `/api/v1/video-settings` | 200 | 10 | Working |
| `/api/v1/linkage-rules` | 200 | 10 | Working |
| `/api/v1/deployments` | 404 | - | No endpoint exists |
| `/api/v1/device-groups` | 200 | 6 | Working |
| `/api/v1/algorithm-services` | 200 | 3 | Working |
| `/api/v1/push-histories` | 200 | 30 | Working |
| `/api/v1/tasks` | 200 | 7 | Working |
| `/api/v1/deployment-schedules` | 200 | - | Working |
| `/api/v1/annotations` | 200 | 15 | Working |

## Details

### 1. `/api/v1/devices` - WORKING
- **Status**: 200 OK
- **Records**: 20 devices
- **Structure**:
```json
{
  "items": [...],
  "total": 20,
  "page": 1,
  "page_size": 20
}
```
- **Frontend Compatible**: Yes - standard pagination format

### 2. `/api/v1/video-settings` - WORKING
- **Status**: 200 OK
- **Records**: 10 settings
- **Structure**:
```json
{
  "total": 10,
  "page": 1,
  "page_size": 20,
  "items": [...]
}
```
- **Frontend Compatible**: Yes

### 3. `/api/v1/linkage-rules` - WORKING
- **Status**: 200 OK
- **Records**: 10 rules
- **Structure**:
```json
{
  "items": [...],
  "total": 10,
  "page": 1,
  "page_size": 20
}
```
- **Frontend Compatible**: Yes

### 4. `/api/v1/deployments` - NOT FOUND
- **Status**: 404 Not Found
- **Error**: `{"detail":"Not Found"}`
- **Notes**: No route registered for `/api/v1/deployments` - needs implementation

### 5. `/api/v1/device-groups` - WORKING
- **Status**: 200 OK
- **Records**: 6 groups
- **Structure**:
```json
{
  "items": [...],
  "total": 6,
  "page": 1,
  "page_size": 20
}
```
- **Frontend Compatible**: Yes

### 6. `/api/v1/algorithm-services` - WORKING
- **Status**: 200 OK
- **Records**: 3 services
- **Notes**: Fixed INET type serialization

### 7. `/api/v1/push-histories` - WORKING
- **Status**: 200 OK
- **Records**: 30 push histories
- **Notes**: Fixed missing table columns, JSONB/datetime serialization

### 8. `/api/v1/tasks` - WORKING
- **Status**: 200 OK
- **Records**: 7 tasks
- **Structure**:
```json
{
  "total": 7,
  "page": 1,
  "page_size": 20,
  "items": [...]
}
```
- **Frontend Compatible**: Yes

### 9. `/api/v1/deployment-schedules` - WORKING
- **Status**: 200 OK
- **Notes**: Fixed TIME type serialization

### 10. `/api/v1/annotations` - WORKING
- **Status**: 200 OK
- **Records**: 15 annotations
- **Notes**: Fixed `polygon_json` field type (dict vs list)

## Database Seed Data Status

| Table | Row Count |
|-------|-----------|
| linkage_rule_device | 74 |
| deployment_device | 24 |
| deployment_schedule | 64 |
| task_device | 98 |
| gb28181_device | 10 |
| onvif_device | 12 |
| preset | 30 |
| annotation | 15 |
| popup_event_limit | 16 |
| clean_record | 10 |
| operation_log | 70 |
| push_history | 30 |
| access_platform | 6 |

## Issues Requiring Attention

1. **deployments endpoint**: No backend route exists - needs implementation
2. All other endpoints verified working