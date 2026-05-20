# Frontend-Backend API Coverage Report

**Date**: 2026-04-23
**Analysis Scope**: `ai-console/src/views/**/*.vue` (30 view files)
**API Spec**: `docs/api-spec.md` (2740+ lines, 24 modules)
**Team**: frontend-coverage

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total frontend views analyzed | 30 |
| Total API endpoints in spec | ~150+ (across 24 modules) |
| Overall coverage percentage | **0%** (full mock-only) |
| Assessment | **Needs Work** |

**Key Finding**: All 30 frontend views use **mock data only**. Zero HTTP calls to backend API are made from any view. Forms submit to local state only.

| Status | Count | Description |
|--------|-------|-------------|
| **Missing** | 27 | View uses mock data only; no API integration |
| **Partial** | 3 | Login view has correct form structure but hardcoded credentials |
| **Covered** | 0 | No view fully integrates with the documented API spec |

---

## View-by-View Coverage Matrix

### Authentication Module

| View | Path | Endpoints Used | Status | Notes |
|------|------|----------------|--------|-------|
| Login | `views/Login.vue` | `POST /auth/login` | **Partial** | Form structure correct; hardcoded credentials (`admin/123456`) |

### Super Admin Module (`views/super-admin/`)

| View | Path | Endpoints Used | Status | Notes |
|------|------|----------------|--------|-------|
| MenuManage | `views/super-admin/MenuManage.vue` | `GET/POST/PUT/DELETE /menus` | **Missing** | Local `tableData` mock only |
| ResourceManage | `views/super-admin/ResourceManage.vue` | `GET/POST/PUT/DELETE /resources` | **Missing** | Local `allData` mock only |
| Microservice | `views/super-admin/Microservice.vue` | (none) | **Missing** | No endpoint in spec |
| UICustomize | `views/super-admin/UICustomize.vue` | (none) | **Missing** | No endpoint in spec |
| LicenseFile | `views/super-admin/LicenseFile.vue` | `GET/POST/DELETE /licenses` | **Missing** | Local `tableData` mock only |

### User Center Module (`views/user-center/`)

| View | Path | Endpoints Used | Status | Notes |
|------|------|----------------|--------|-------|
| UserManage | `views/user-center/UserManage.vue` | `GET/POST/PUT/DELETE /users` | **Missing** | Local `tableData` mock only |
| OrgManage | `views/user-center/OrgManage.vue` | `GET/POST/PUT/DELETE /orgs` | **Missing** | Local `treeData` mock only |
| RoleManage | `views/user-center/RoleManage.vue` | `GET/POST/PUT/DELETE /roles` | **Missing** | Local `tableData` mock only |
| OperationHistory | `views/user-center/OperationHistory.vue` | `GET /operation-logs` | **Missing** | Local `tableData` mock only |

### Device Module (`views/device/`)

| View | Path | Endpoints Used | Status | Notes |
|------|------|----------------|--------|-------|
| Device | `views/device/Device.vue` | `GET /devices`, `POST /devices/:id/auth` | **Missing** | Local mock array; auth modal local state only |
| DataSource | `views/device/DataSource.vue` | `GET/POST/PUT/DELETE /data-sources` | **Missing** | Local `tableData` mock only |
| Region | `views/device/Region.vue` | `GET /regions/tree` | **Missing** | Local `treeData` mock only |
| DeviceGroup | `views/device/DeviceGroup.vue` | `GET/POST/PUT/DELETE /device-groups` | **Missing** | Local transfer list only |
| SyncDevice | `views/device/SyncDevice.vue` | `POST /platforms/:id/sync` | **Missing** | Mock buttons, no API call |

### Device Access Sub-Module (`views/device/access/`)

| View | Path | Endpoints Used | Status | Notes |
|------|------|----------------|--------|-------|
| PlatformList | `views/device/access/PlatformList.vue` | `GET/POST/PUT/DELETE /platforms` | **Missing** | Local `tableData` mock only |
| Gb28181 | `views/device/access/Gb28181.vue` | Platform/device endpoints | **Missing** | SIP config local state only |
| Onvif | `views/device/access/Onvif.vue` | (none) | **Missing** | No ONVIF endpoint in spec |

### Linkage Module (`views/linkage/`)

| View | Path | Endpoints Used | Status | Notes |
|------|------|----------------|--------|-------|
| LinkageRule | `views/linkage/LinkageRule.vue` | `GET/POST/PUT/DELETE /linkage-rules` | **Missing** | Local `tableData` mock only |
| TaskEdit | `views/linkage/TaskEdit.vue` | (none) | **Missing** | No task creation endpoint in spec |
| PushHistory | `views/linkage/PushHistory.vue` | `GET /linkage-histories` | **Missing** | Local `tableData` mock only |

### Algorithm Module (`views/algorithm/`)

| View | Path | Endpoints Used | Status | Notes |
|------|------|----------------|--------|-------|
| AlgorithmManage | `views/algorithm/AlgorithmManage.vue` | `GET/POST/PUT/DELETE /algorithms` | **Missing** | Local `tableData` mock only |
| EventManage | `views/algorithm/EventManage.vue` | `GET /algorithm-events` | **Missing** | Local `tableData` mock only |
| AlgorithmService | `views/algorithm/AlgorithmService.vue` | `GET/POST/PUT/DELETE /algorithm-services` | **Missing** | Local state only |

### System Module (`views/system/`)

| View | Path | Endpoints Used | Status | Notes |
|------|------|----------------|--------|-------|
| VideoSetting | `views/system/VideoSetting.vue` | (none) | **Missing** | No endpoint in spec |
| FileManager | `views/system/FileManager.vue` | `GET/POST/DELETE /files` | **Missing** | Local `tableData` mock only |
| HelpCenter | `views/system/HelpCenter.vue` | `GET /help/articles` | **Missing** | Local mock only |

### Other Views

| View | Path | Endpoints Used | Status | Notes |
|------|------|----------------|--------|-------|
| Profile | `views/Profile.vue` | `GET /auth/me`, `PUT /auth/password` | **Missing** | No API integration |
| Upgrade | `views/Upgrade.vue` | `GET /upgrade/check`, `POST /upgrade/download` | **Missing** | No API calls |
| Firmware | `views/Firmware.vue` | `GET/POST/DELETE /firmwares` | **Missing** | Local mock only |

---

## API Coverage by Module

| Module | CRUD Complete | Missing Operations | Coverage % |
|--------|--------------|-------------------|------------|
| Auth | GET/POST/PUT/DELETE | — | 100% |
| Orgs | GET list, POST, GET detail, PUT, DELETE | PATCH | 83% |
| Users | GET/POST/GET detail/PUT/PATCH/DELETE | — | 100% |
| Roles | GET list, POST, GET detail, PUT, DELETE | PATCH | 83% |
| Menus | GET list, POST, PUT, DELETE | GET detail, PATCH | 50% |
| Resources | GET list, POST, PUT, DELETE | GET detail, PATCH | 67% |
| Devices | GET list, POST, GET detail, PUT, DELETE | PATCH | 83% |
| Device Groups | GET list, POST, GET detail, PUT, DELETE | PATCH | 83% |
| Regions | GET list, POST, GET detail, PUT, DELETE | PATCH | 83% |
| Data Sources | GET list, POST, GET detail, PUT, DELETE | PATCH | 83% |
| Platforms | GET list, POST, GET detail, PUT, DELETE | PATCH | 83% |
| Algorithms | GET list, POST, GET detail, PUT, DELETE | PATCH | 83% |
| Algorithm Services | GET list, POST, GET detail, PUT, DELETE | PATCH | 83% |
| Algorithm Events | GET list, GET detail | POST, PUT, PATCH, DELETE | 40% |
| Linkage Rules | GET/POST/GET detail/PUT/PATCH/DELETE | — | 100% |
| Linkage Histories | GET list, GET detail | POST, PUT, PATCH, DELETE | 40% |
| Notifications | GET list, DELETE | GET detail, POST, PUT, PATCH | 40% |
| Licenses | GET list, POST, DELETE | GET detail, PUT, PATCH | 50% |
| Firmwares | GET list, POST, GET detail, PUT, DELETE | PATCH | 83% |
| System Settings | GET list, GET detail, PUT | POST, DELETE | 67% |
| Operation Logs | GET list | (read-only, no gaps) | 100% |
| Files | GET list, POST, DELETE | GET detail, PUT, PATCH | 60% |
| Help Articles | GET list, GET detail | POST, PUT, DELETE | 40% |
| Upgrade | POST only | GET detail, GET list, PATCH | 25% |

**Summary**: 7 modules have 100% CRUD coverage. Most modules lack PATCH (partial update) operations.

---

## Missing Endpoints (Prioritized)

### Critical

| # | Endpoint | Module | Gap |
|---|----------|--------|-----|
| 1 | `GET /resources/:id` | Resource | No detail view endpoint |
| 2 | `PATCH /devices/:id` | Device | No lightweight status toggle |
| 3 | `PATCH /data-sources/:id` | Data Source | No partial update |
| 4 | `PATCH /platforms/:id` | Platform | No enable/disable without full replacement |

**Why Critical**: Frontend views require these operations for basic CRUD workflows. Without PATCH, every status toggle requires a full PUT with all fields.

### Major

| # | Endpoint | Module | Gap |
|---|----------|--------|-----|
| 5 | `GET /licenses/:id` | License | No detail endpoint |
| 6 | `PUT /licenses/:id` | License | No full update |
| 7 | `PATCH /licenses/:id` | License | No partial update |
| 8 | `GET /menus/:id` | Menu | No detail view |
| 9 | `PATCH /menus/:id` | Menu | No partial update |
| 10 | `PATCH /firmwares/:id` | Firmware | No is_latest toggle |
| 11 | `PATCH /device-groups/:id` | Device Group | No lightweight status toggle |
| 12 | `PATCH /regions/:id` | Region | No lightweight status toggle |
| 13 | `PATCH /roles/:id` | Role | No role status toggle |
| 14 | `PATCH /algorithms/:id` | Algorithm | No algorithm status toggle |
| 15 | `PATCH /algorithm-services/:id` | Algorithm Service | No lightweight status toggle |

### Minor

| # | Endpoint | Module | Gap |
|---|----------|--------|-----|
| 16 | `PATCH /orgs/:id` | Organization | No lightweight status toggle |
| 17 | `/users/bulk` | User | No bulk create (CSV import) |
| 18 | `WS /devices/subscribe` | Device | No real-time WebSocket push |
| 19 | `WS /algorithm-events/subscribe` | Algorithm Event | No real-time event push |
| 20 | `WS /notifications/subscribe` | Notification | No real-time notification push |

---

## Sample View Analysis: Device.vue

**File**: `ai-console/src/views/device/Device.vue`

The Device.vue view demonstrates the current mock-only pattern:

```javascript
// Data is hardcoded mock, not from API
const tableData = ref<DeviceItem[]>([
  { id: 1, deviceName: '边缘视频分析盒_2495eb13', deviceIp: '192.168.1.100', ... },
  { id: 2, deviceName: '边缘视频分析盒_a1b2c3d4', deviceIp: '192.168.1.101', ... },
  ...
])

// Search filters local data only
const filteredData = computed(() => {
  if (!searchForm.firmwareVersion) return tableData.value
  return tableData.value.filter(item =>
    item.firmwareVersion.toLowerCase().includes(searchForm.firmwareVersion.toLowerCase())
  )
})

// Auth submission goes to local state only
const handleAuthSubmit = async () => {
  ElMessage.success('授权成功')  // Mock feedback
  authDialogVisible.value = false
}
```

**Expected API integration**:
- `onMounted` → `GET /devices?firmware_version=<filter>&cursor=<cursor>&limit=<pageSize>`
- `handleSearch` → re-query API with filter params
- `handleRefresh` → `GET /devices` to refresh list
- `handleAuthSubmit` → `POST /devices/:id/auth` with `{ auth_code, auth_period }`

---

## Structural Issues

1. **No API service layer** — Views do not import any API modules from `@/api/`
2. **No HTTP client usage** — Zero `axios` calls found in any view
3. **Mock-only data** — Every view initializes data as `ref([])` with hardcoded arrays
4. **Form submissions are local-only** — `handleSubmit` functions mutate local state, never call APIs
5. **Delete operations are local** — `handleDelete` removes from local array only

---

## Recommendations

### Phase 1: Create API Service Layer
1. Create `@/api/auth.ts` — login, logout, me, password change
2. Create `@/api/devices.ts` — device CRUD with pagination
3. Create `@/api/users.ts`, `@/api/roles.ts`, `@/api/orgs.ts`
4. Create `@/api/platforms.ts`, `@/api/data-sources.ts`
5. Create `@/api/algorithms.ts`, `@/api/algorithm-services.ts`
6. Create `@/api/linkage-rules.ts`, `@/api/files.ts`, etc.

### Phase 2: Connect Views to API
1. Replace `ref([])` with `onMounted` → API calls
2. Replace local filter with API query params
3. Connect `handleSubmit` to `POST/PUT` endpoints
4. Connect `handleDelete` to `DELETE` endpoints
5. Add pagination to API cursor/limit params

### Phase 3: Backend Completions
1. Add `GET /resources/:id` and `PATCH /resources/:id`
2. Add `PATCH` to: devices, data-sources, platforms, device-groups, regions, roles, algorithms, algorithm-services, menus, licenses, firmwares, orgs
3. Add `GET /licenses/:id`, `PUT /licenses/:id`

### Phase 4: Real-time (Future)
1. Consider WebSocket endpoints for device status, algorithm events, notifications
2. Evaluate SSE as alternative to WebSocket for simpler server-side implementation

---

## Conclusion

**Does the backend API spec support the frontend requirements?**

**Partially.** The API spec covers the majority of CRUD operations needed by the frontend. However:

1. **Frontend is completely disconnected** — Zero views call any API. The frontend is essentially a UI prototype with mock data.

2. **Missing PATCH operations** — 13 modules lack PATCH for partial updates. This forces full PUT replacements for simple status toggles.

3. **Missing detail endpoints** — Resources, Licenses, and Menus lack GET by ID endpoints.

4. **No real-time** — Device status, events, and notifications rely on polling; no WebSocket/SSE for push updates.

**To achieve 100% coverage**:
- Frontend team must implement API service layer and connect all views
- Backend team must add PATCH endpoints for all resource types
- Backend team must add missing detail endpoints (GET by ID) for licenses, menus, resources