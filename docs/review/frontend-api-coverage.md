# Frontend API Coverage Matrix

**Generated:** 2026-04-23
**Analysis Scope:** `ai-console/src/views/**/*.vue` (30 view files)
**API Spec:** `docs/api-spec.md`

---

## Summary

| Status | Count | Description |
|--------|-------|-------------|
| **Missing** | 27 | View uses mock data only; API endpoints not implemented |
| **Partial** | 3 | Login view has correct API structure but uses hardcoded credentials |
| **Covered** | 0 | No view fully integrates with the documented API spec |

**Key Finding:** All frontend views currently use **mock data only** (local `ref` arrays with hardcoded sample records). No view makes actual HTTP calls to the backend API. Forms submit to local state only, not to any API endpoint.

---

## Detailed Coverage by View

### Authentication

| View | Path | API Needed | Status | Notes |
|------|------|-----------|--------|-------|
| Login | `views/Login.vue` | `POST /auth/login` | **Partial** | Form structure matches API but uses hardcoded credentials (`admin/123456`) instead of actual API call |

### Super Admin Module (`views/super-admin/`)

| View | Path | API Needed | Status | Notes |
|------|------|-----------|--------|-------|
| MenuManage | `views/super-admin/MenuManage.vue` | `GET/POST/PUT/DELETE /menus` | **Missing** | All CRUD operations use local `tableData` mock array |
| ResourceManage | `views/super-admin/ResourceManage.vue` | `GET/POST/PUT/DELETE /resources` | **Missing** | All CRUD operations use local `allData` mock array |
| Microservice | `views/super-admin/Microservice.vue` | (no documented endpoint) | **Missing** | Local `tableData` mock; no API endpoint exists in spec |
| UICustomize | `views/super-admin/UICustomize.vue` | (no documented endpoint) | **Missing** | Local `tableData` mock; platform customization has no API |
| LicenseFile | `views/super-admin/LicenseFile.vue` | `GET/POST/DELETE /licenses` | **Missing** | All operations use local `tableData` mock |

### User Center Module (`views/user-center/`)

| View | Path | API Needed | Status | Notes |
|------|------|-----------|--------|-------|
| UserManage | `views/user-center/UserManage.vue` | `GET/POST/PUT/DELETE /users` | **Missing** | All CRUD use local `tableData`; role changes update local state only |
| OrgManage | `views/user-center/OrgManage.vue` | `GET/POST/PUT/DELETE /orgs` | **Missing** | Tree operations use local `treeData` mock; no API calls |
| RoleManage | `views/user-center/RoleManage.vue` | `GET/POST/PUT/DELETE /roles` | **Missing** | All CRUD use local `tableData`; permission tree is local mock |
| OperationHistory | `views/user-center/OperationHistory.vue` | `GET /operation-logs` | **Missing** | Uses local `tableData` mock; no API integration |

### Device Module (`views/device/`)

| View | Path | API Needed | Status | Notes |
|------|------|-----------|--------|-------|
| Device | `views/device/Device.vue` | `GET /devices`, `POST /devices/:id/auth` | **Missing** | Shows device list with authorization modal; all data is local mock |
| DataSource | `views/device/DataSource.vue` | `GET/POST/PUT/DELETE /data-sources` | **Missing** | All CRUD use local `tableData` mock |
| Region | `views/device/Region.vue` | `GET /regions/tree` | **Missing** | Tree display uses local `treeData` mock only |
| DeviceGroup | `views/device/DeviceGroup.vue` | `GET/POST/PUT/DELETE /device-groups` | **Missing** | Device assignment uses local `allDevices` transfer list |
| SyncDevice | `views/device/SyncDevice.vue` | `POST /platforms/:id/sync` | **Missing** | Sync operations are mock buttons with no API call |

### Device Access Sub-Module (`views/device/access/`)

| View | Path | API Needed | Status | Notes |
|------|------|-----------|--------|-------|
| PlatformList | `views/device/access/PlatformList.vue` | `GET/POST/PUT/DELETE /platforms` | **Missing** | All CRUD use local `tableData` mock |
| Gb28181 | `views/device/access/Gb28181.vue` | Platform and device endpoints | **Missing** | SIP config, platform list, device list all use local state |
| Onvif | `views/device/access/Onvif.vue` | (no documented endpoint) | **Missing** | ONVIF device discovery/search not in API spec |

### Linkage Module (`views/linkage/`)

| View | Path | API Needed | Status | Notes |
|------|------|-----------|--------|-------|
| LinkageRule | `views/linkage/LinkageRule.vue` | `GET/POST/PUT/DELETE /linkage-rules` | **Missing** | All CRUD use local `tableData` mock |
| TaskEdit | `views/linkage/TaskEdit.vue` | (no documented endpoint) | **Missing** | Task/edit form with no API; linkage task creation not in spec |
| PushHistory | `views/linkage/PushHistory.vue` | `GET /linkage-histories` | **Missing** | Uses local `tableData` mock; no API integration |

### Algorithm Module (`views/algorithm/`)

| View | Path | API Needed | Status | Notes |
|------|------|-----------|--------|-------|
| AlgorithmManage | `views/algorithm/AlgorithmManage.vue` | `GET/POST/PUT/DELETE /algorithms` | **Missing** | All CRUD use local `tableData` mock |
| EventManage | `views/algorithm/EventManage.vue` | `GET /algorithm-events` | **Missing** | Uses local `tableData` mock; event CRUD not fully in spec |
| AlgorithmService | `views/algorithm/AlgorithmService.vue` | `GET/POST/PUT/DELETE /algorithm-services` | **Missing** | Service management uses local state; address management local |

### System Module (`views/system/`)

| View | Path | API Needed | Status | Notes |
|------|------|-----------|--------|-------|
| VideoSetting | `views/system/VideoSetting.vue` | (no documented endpoint) | **Missing** | Recording rules management; no API endpoint in spec |
| FileManager | `views/system/FileManager.vue` | `GET/POST/DELETE /files` | **Missing** | File CRUD use local `tableData` mock |
| PopupSetting | `views/system/PopupSetting.vue` | (not found in glob) | — | View file not located |
| DisposeTag | `views/system/DisposeTag.vue` | (not found in glob) | — | View file not located |
| HelpCenter | `views/system/HelpCenter.vue` | `GET /help/articles` | **Missing** | Help articles display uses local mock |

### Other Views

| View | Path | API Needed | Status | Notes |
|------|------|-----------|--------|-------|
| Profile | `views/Profile.vue` | `GET /auth/me`, `PUT /auth/password` | **Missing** | User profile view with no API integration |
| Upgrade | `views/Upgrade.vue` | `GET /upgrade/check`, `POST /upgrade/download` | **Missing** | Upgrade check and download UI with no API calls |
| Firmware | `views/Firmware.vue` | `GET/POST/DELETE /firmwares` | **Missing** | Firmware list management with local mock |
| Console | `views/Console.vue` | (not found in glob) | — | View file not located |
| Events | `views/Events.vue` | (not found in glob) | — | View file not located |
| DataClean | `views/DataClean.vue` | (not found in glob) | — | View file not located |
| MenuPanel | `views/MenuPanel.vue` | (not found in glob) | — | View file not located |

### Monitor Module (`views/monitor/`)

| View | Path | API Needed | Status | Notes |
|------|------|-----------|--------|-------|
| MonitorWall | `views/monitor/MonitorWall.vue` | (not found in glob) | — | View file not located |
| MonitorSingle | `views/monitor/MonitorSingle.vue` | (not found in glob) | — | View file not located |
| FileAnalysis | `views/monitor/FileAnalysis.vue` | (not found in glob) | — | View file not located |

### Event Stats Module (`views/event-stats/`)

| View | Path | API Needed | Status | Notes |
|------|------|-----------|--------|-------|
| EventStats | `views/event-stats/EventStats.vue` | (not found in glob) | — | View file not located |

### Event Manage Module (`views/event-manage/`)

| View | Path | API Needed | Status | Notes |
|------|------|-----------|--------|-------|
| EventManage | `views/event-manage/EventManage.vue` | (not found in glob) | — | View file not located |

### Deployment Module (`views/deployment/`)

| View | Path | API Needed | Status | Notes |
|------|------|-----------|--------|-------|
| Deployment | `views/deployment/Deployment.vue` | (not found in glob) | — | View file not located |
| Annotation | `views/deployment/Annotation.vue` | (not found in glob) | — | View file not located |

---

## API Endpoints from Spec

| Endpoint Category | Endpoints | Frontend Coverage |
|-------------------|-----------|-------------------|
| **Auth** | `/auth/login`, `/auth/me`, `/auth/password`, `/auth/sessions` | Partial (login form exists) |
| **Users** | `/users`, `/users/:id`, `/users/:id/password`, `/users/:id/operations` | None |
| **Orgs** | `/orgs`, `/orgs/:id`, `/orgs/tree`, `/orgs/:id/users` | None |
| **Roles** | `/roles`, `/roles/:id`, `/roles/:id/users` | None |
| **Menus** | `/menus`, `/menus/:id` | None |
| **Resources** | `/resources`, `/resources/:id` | None |
| **Devices** | `/devices`, `/devices/:id`, `/devices/:id/stats`, `/devices/:id/auth`, `/devices/:id/video-sources`, `/devices/export`, `/devices/batch-delete`, `/devices/batch-update` | None |
| **Device Groups** | `/device-groups`, `/device-groups/:id`, `/device-groups/:id/devices`, `/device-groups/tree` | None |
| **Regions** | `/regions`, `/regions/:id`, `/regions/tree` | None |
| **Data Sources** | `/data-sources`, `/data-sources/:id`, `/data-sources/:id/test` | None |
| **Platforms** | `/platforms`, `/platforms/:id`, `/platforms/:id/sync`, `/platforms/:id/sync-status` | None |
| **Algorithms** | `/algorithms`, `/algorithms/:id`, `/algorithms/:id/deploy` | None |
| **Algorithm Services** | `/algorithm-services`, `/algorithm-services/:id`, `/algorithm-services/:id/start`, `/algorithm-services/:id/stop`, `/algorithm-services/:id/stats` | None |
| **Algorithm Events** | `/algorithm-events`, `/algorithm-events/:id`, `/algorithm-events/:id/handle`, `/algorithm-events/batch-handle`, `/algorithm-events/stats` | None |
| **Linkage Rules** | `/linkage-rules`, `/linkage-rules/:id`, `/linkage-rules/:id/test` | None |
| **Linkage Histories** | `/linkage-histories`, `/linkage-histories/:id` | None |
| **Notifications** | `/notifications`, `/notifications/:id/read`, `/notifications/read-all`, `/notifications/:id` | None |
| **Licenses** | `/licenses`, `/licenses/verify`, `/licenses/:id` | None |
| **Firmwares** | `/firmwares`, `/firmwares/:id`, `/firmwares/:id/upgrade` | None |
| **System Settings** | `/system-settings`, `/system-settings/:key` | None |
| **Operation Logs** | `/operation-logs`, `/operation-logs/export` | None |
| **Files** | `/files`, `/files/:id/download` | None |
| **Help** | `/help/articles`, `/help/articles/:id` | None |
| **Upgrade** | `/upgrade/check`, `/upgrade/download`, `/upgrade/download-status` | None |

---

## Gap Analysis

### Critical Gaps (No API Coverage)
1. **All device management views** — devices, data sources, regions, device groups have no API integration
2. **All user/role/org management views** — full admin CRUD operations are mock-only
3. **All algorithm management views** — algorithms, events, services have no API calls
4. **All linkage views** — rules and push history are completely disconnected from API
5. **All system views** — file manager, video settings, help center use local data only

### Missing API Endpoints (Not in Spec)
The following frontend features have **no corresponding endpoint** in the API spec:
- **Microservice management** — `Microservice.vue` manages internal services with no API
- **UI Customize** — Platform branding/theme configuration has no API
- **License file upload** — License management exists but file upload endpoint unclear
- **ONVIF device discovery** — Search/discovery protocol not in API spec
- **Video recording settings** — Rule-based recording config has no endpoint
- **Sync device operations** — Tenant-based device sync has no endpoint
- **Task/Linkage edit form** — Task creation/configuration not documented

### Structural Issues
1. **No API service layer** — Views do not import any API modules from `@/api/`
2. **No HTTP client usage** — Zero `axios` calls found in any view
3. **Mock-only data** — Every view initializes data as `ref([])` with hardcoded arrays
4. **Form submissions are local-only** — `handleSubmit` functions mutate local state, never call APIs
5. **Delete operations are local** — `handleDelete` removes from local array only

---

## Recommendations

1. **Create API service layer** — Establish `@/api/` modules for each domain (auth, users, devices, etc.)
2. **Replace mock data** — Replace `ref([])` initializations with API calls in `onMounted`
3. **Connect form submissions** — `handleSubmit` should `POST`/`PUT` to API endpoints
4. **Connect delete operations** — `handleDelete` should `DELETE` via API
5. **Add pagination integration** — Connect table pagination to API cursor/limit params
6. **Add search/filter integration** — Connect search forms to API query params
7. **Document missing endpoints** — Spec needs endpoints for microservice, UI customize, ONVIF, video settings
