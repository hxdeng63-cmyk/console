# Missing API Endpoints — Coverage Analysis

**Date**: 2026-04-23
**Analyzed**: `docs/api-spec.md` (2740+ lines, 24 modules)

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 4 |
| Major | 9 |
| Minor | 5 |

---

## Severity Definitions

- **Critical**: Frontend NEEDS this endpoint — no API exists at all
- **Major**: API exists but is incomplete (missing pagination, PATCH, etc.)
- **Minor**: Nice-to-have; API design could be enhanced

---

## Critical Gaps

### 1. `/resources` — Missing CRUD Operations
**Module**: Resource (`/resources`)

| Operation | Status | Notes |
|-----------|--------|-------|
| GET /resources | OK | Supports pagination, filter by `resource_type` |
| POST /resources | OK | |
| GET /resources/:id | **MISSING** | No detail endpoint |
| PUT /resources/:id | OK | |
| PATCH /resources/:id | **MISSING** | No partial update (e.g., status toggle) |
| DELETE /resources/:id | OK | |

**Gap**: No `GET /resources/:id` or `PATCH /resources/:id`. Frontend cannot view resource details or toggle status without a full update.

---

### 2. `/data-sources` — Missing PATCH
**Module**: Data Source (`/data-sources`)

| Operation | Status | Notes |
|-----------|--------|-------|
| GET /data-sources | OK | Pagination + `device_id`, `type`, `status` filters |
| POST /data-sources | OK | |
| GET /data-sources/:id | OK | |
| PUT /data-sources/:id | OK | |
| PATCH /data-sources/:id | **MISSING** | No partial update for status changes |
| DELETE /data-sources/:id | OK | |

**Gap**: No `PATCH /data-sources/:id` for quick status toggle (e.g., enable/disable a data source without sending full update).

---

### 3. `/devices` — Missing PATCH
**Module**: Device (`/devices`)

| Operation | Status | Notes |
|-----------|--------|-------|
| GET /devices | OK | Pagination + `firmware_version`, `department`, `online_status`, `keyword` filters |
| POST /devices | OK | |
| GET /devices/:id | OK | |
| PUT /devices/:id | OK | |
| PATCH /devices/:id | **MISSING** | No partial update |
| DELETE /devices/:id | OK | |

**Gap**: No `PATCH /devices/:id` for lightweight updates (e.g., quick status/department change).

---

### 4. `/platforms` — Missing PATCH
**Module**: Platform Access (`/platforms`)

| Operation | Status | Notes |
|-----------|--------|-------|
| GET /platforms | OK | Pagination + `platform_type` filter |
| POST /platforms | OK | |
| GET /platforms/:id | OK | |
| PUT /platforms/:id | OK | |
| PATCH /platforms/:id | **MISSING** | No partial update |
| DELETE /platforms/:id | OK | |

**Gap**: No `PATCH /platforms/:id` for enabling/disabling a platform without full replacement.

---

## Major Gaps

### 5. `/data-sources/:id` — No Detail with Associated Device Info
**Module**: Data Source

`GET /data-sources/:id` returns the data source, but the response does not include computed fields like `device_name` in the detail view (only listed on the list endpoint). The detail response should mirror or extend the list item shape.

**Current detail response** lacks: `device_name` (only `device_id` is returned).

---

### 6. `/licenses` — Missing Detail Endpoint
**Module**: License (`/licenses`)

| Operation | Status | Notes |
|-----------|--------|-------|
| GET /licenses | OK | Pagination + `status` filter |
| POST /licenses | OK | |
| GET /licenses/:id | **MISSING** | No detail endpoint |
| PUT /licenses/:id | **MISSING** | No full update |
| PATCH /licenses/:id | **MISSING** | No partial update |
| DELETE /licenses/:id | OK | |

**Gap**: Cannot retrieve or update a single license by ID. Only list and delete are available.

---

### 7. `/firmwares` — Missing Detail Endpoint
**Module**: Firmware (`/firmwares`)

| Operation | Status | Notes |
|-----------|--------|-------|
| GET /firmwares | OK | Pagination + `product_type` filter |
| POST /firmwares | OK | |
| GET /firmwares/:id | OK | |
| PUT /firmwares/:id | OK | |
| PATCH /firmwares/:id | **MISSING** | No partial update (e.g., toggle `is_latest`) |
| DELETE /firmwares/:id | OK | |

**Gap**: No `PATCH /firmwares/:id` for toggling `is_latest` flag or updating `release_note` without sending the whole firmware file.

---

### 8. `/device-groups` — Missing PATCH
**Module**: Device Group (`/device-groups`)

| Operation | Status | Notes |
|-----------|--------|-------|
| GET /device-groups | OK | Pagination + `region_id`, `keyword` filters |
| POST /device-groups | OK | |
| GET /device-groups/:id | OK | |
| PUT /device-groups/:id | OK | |
| PATCH /device-groups/:id | **MISSING** | No partial update |
| DELETE /device-groups/:id | OK | |

**Gap**: No lightweight status toggle.

---

### 9. `/regions` — Missing PATCH
**Module**: Region (`/regions`)

| Operation | Status | Notes |
|-----------|--------|-------|
| GET /regions | OK | Pagination + `status` filter |
| POST /regions | OK | |
| GET /regions/:id | OK | |
| PUT /regions/:id | OK | |
| PATCH /regions/:id | **MISSING** | No partial update |
| DELETE /regions/:id | OK | |

**Gap**: No lightweight status toggle.

---

### 10. `/menus` — Missing PATCH
**Module**: Menu (`/menus`)

| Operation | Status | Notes |
|-----------|--------|-------|
| GET /menus | OK | Pagination + `status` filter |
| POST /menus | OK | |
| GET /menus/:id | **MISSING** | No detail endpoint |
| PUT /menus/:id | OK | |
| PATCH /menus/:id | **MISSING** | No partial update |
| DELETE /menus/:id | OK | |

**Gap**: No detail view or PATCH for menus.

---

### 11. `/roles` — Missing PATCH
**Module**: Role (`/roles`)

| Operation | Status | Notes |
|-----------|--------|-------|
| GET /roles | OK | Pagination + `keyword`, `status` filters |
| POST /roles | OK | |
| GET /roles/:id | OK | |
| PUT /roles/:id | OK | |
| PATCH /roles/:id | **MISSING** | No partial update |
| DELETE /roles/:id | OK | |

**Gap**: No PATCH for quick role status toggle.

---

### 12. `/algorithms` — Missing PATCH
**Module**: Algorithm (`/algorithms`)

| Operation | Status | Notes |
|-----------|--------|-------|
| GET /algorithms | OK | Pagination + `type`, `status` filters |
| POST /algorithms | OK | |
| GET /algorithms/:id | OK | |
| PUT /algorithms/:id | OK | |
| PATCH /algorithms/:id | **MISSING** | No partial update |
| DELETE /algorithms/:id | OK | |

**Gap**: No lightweight status toggle for algorithms.

---

### 13. `/algorithm-services` — Missing PATCH
**Module**: Algorithm Service (`/algorithm-services`)

| Operation | Status | Notes |
|-----------|--------|-------|
| GET /algorithm-services | OK | Pagination + `device_id`, `algorithm_id`, `status` filters |
| POST /algorithm-services | OK | |
| GET /algorithm-services/:id | OK | |
| PUT /algorithm-services/:id | OK | |
| PATCH /algorithm-services/:id | **MISSING** | No partial update |
| DELETE /algorithm-services/:id | OK | |

**Gap**: No lightweight status toggle (though `start`/`stop` actions exist, a PATCH for status would be more RESTful).

---

## Minor Gaps

### 14. `/orgs` — Missing PATCH
**Module**: Organization (`/orgs`)

| Operation | Status | Notes |
|-----------|--------|-------|
| GET /orgs | OK | Pagination + `parent_id`, `status` filters |
| POST /orgs | OK | |
| GET /orgs/:id | OK | |
| PUT /orgs/:id | OK | |
| PATCH /orgs/:id | **MISSING** | No partial update |
| DELETE /orgs/:id | OK | |

**Gap**: No lightweight status toggle for orgs.

---

### 15. `/users` — No Bulk Create
**Module**: User (`/users`)

Only single user creation is available. No bulk user import (e.g., from CSV).

---

### 16. `/devices` — No Real-time Subscription Endpoint
**Module**: Device (`/devices`)

The spec defines REST polling only. No WebSocket/SSE endpoint for real-time device status push (heartbeat updates, online/offline events).

---

### 17. `/algorithm-events` — No Real-time Subscription Endpoint
**Module**: Algorithm Event (`/algorithm-events`)

No WebSocket/SSE for real-time event push.

---

### 18. `/notifications` — No Real-time Subscription Endpoint
**Module**: Notification (`/notifications`)

No WebSocket/SSE for real-time notification push. The `unread_count` in list response implies polling.

---

## Complete CRUD Coverage Matrix

| Module | GET list | POST | GET detail | PUT | PATCH | DELETE |
|--------|----------|------|------------|-----|-------|--------|
| Auth | OK | OK | OK | OK | - | OK |
| Orgs | OK | OK | OK | OK | **MISSING** | OK |
| Users | OK | OK | OK | OK | OK | OK |
| Roles | OK | OK | OK | OK | **MISSING** | OK |
| Menus | OK | OK | **MISSING** | OK | **MISSING** | OK |
| Resources | OK | OK | **MISSING** | OK | **MISSING** | OK |
| Devices | OK | OK | OK | OK | **MISSING** | OK |
| Device Groups | OK | OK | OK | OK | **MISSING** | OK |
| Regions | OK | OK | OK | OK | **MISSING** | OK |
| Data Sources | OK | OK | OK | OK | **MISSING** | OK |
| Platforms | OK | OK | OK | OK | **MISSING** | OK |
| Algorithms | OK | OK | OK | OK | **MISSING** | OK |
| Algorithm Services | OK | OK | OK | OK | **MISSING** | OK |
| Algorithm Events | OK | - | OK | - | - | - |
| Linkage Rules | OK | OK | OK | OK | OK | OK |
| Linkage Histories | OK | - | OK | - | - | - |
| Notifications | OK | - | - | - | - | OK |
| Licenses | OK | OK | **MISSING** | **MISSING** | **MISSING** | OK |
| Firmwares | OK | OK | OK | OK | **MISSING** | OK |
| System Settings | OK | - | OK | OK | - | - |
| Operation Logs | OK | - | - | - | - | - |
| Files | OK | OK | - | - | - | OK |
| Help Articles | OK | - | OK | - | - | - |
| Upgrade | - | OK | - | - | - | - |

---

## Recommendations

### Immediate (Critical)
1. Add `GET /resources/:id` — needed for resource detail view
2. Add `PATCH /devices/:id` — needed for device status toggle
3. Add `PATCH /data-sources/:id` — needed for data source enable/disable
4. Add `PATCH /platforms/:id` — needed for platform enable/disable

### Short-term (Major)
5. Add `GET /licenses/:id`, `PUT /licenses/:id`, `PATCH /licenses/:id` — license management is incomplete
6. Add `PATCH /menus/:id` and `GET /menus/:id` — menu management missing detail and partial update
7. Add `PATCH /firmwares/:id` — for toggling `is_latest`
8. Add `PATCH` to device-groups, regions, roles, algorithms, algorithm-services for status toggles

### Nice-to-have (Minor)
9. WebSocket/SSE endpoints for real-time: devices, algorithm-events, notifications
10. Bulk user import (CSV)
