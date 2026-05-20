# Frontend-Backend Coverage Report

**Date**: 2026-04-23
**Team**: frontend-coverage

---

## Executive Summary

The ai-console frontend is entirely disconnected from the backend API. All 30 view files use mock data; zero HTTP calls to documented API endpoints exist in the codebase. The API spec is well-structured with cursor-based pagination and consistent response envelopes, but has critical gaps (missing PATCH on most modules, missing detail endpoints) and design inconsistencies (wrong 201 status, inconsistent status-update patterns). The database schema aligns at ~80% with the API but has its own critical issues (missing FKs, unscalable partitioning).

---

## Source Documents

| Document | Owner | Key Findings |
|----------|-------|--------------|
| `frontend-api-coverage.md` | frontend-mapper | 27 views missing API, 3 partial, 0 fully covered |
| `api-spec-review.md` | api-spec-reviewer | 5 critical issues, 4 major, 5 minor |
| `db-schema-review.md` | db-reviewer | 5 critical issues, 13 major, 10 minor |
| `missing-api-endpoints.md` | api-analyst | 4 critical gaps, 9 major, 5 minor |

---

## Part 1: Frontend State

### Views with Mock Data Only (Critical)

**All 30 views use local `ref([])` arrays with hardcoded sample records.** No view imports API modules, makes axios calls, or connects forms to endpoints.

#### Affected Modules

| Module | Views | Status |
|--------|-------|--------|
| Super Admin | MenuManage, ResourceManage, Microservice, UICustomize, LicenseFile | All mock |
| User Center | UserManage, OrgManage, RoleManage, OperationHistory | All mock |
| Device | Device, DataSource, Region, DeviceGroup, SyncDevice | All mock |
| Device Access | PlatformList, Gb28181, Onvif | All mock |
| Linkage | LinkageRule, TaskEdit, PushHistory | All mock |
| Algorithm | AlgorithmManage, EventManage, AlgorithmService | All mock |
| System | VideoSetting, FileManager, PopupSetting, DisposeTag, HelpCenter | All mock or not found |
| Auth | Login | Partial (form structure matches API, but hardcoded credentials) |

### Structural Issues

1. **No API service layer** — no `@/api/` modules imported in any view
2. **No HTTP client usage** — zero `axios` calls found across all views
3. **Mock-only data** — all `tableData` initialized as `ref([])` with hardcoded arrays
4. **Forms mutate local state** — `handleSubmit` updates local array, never calls API
5. **Delete operations are local** — `handleDelete` splices local array only

### Features with No API at All

These views reference functionality not documented in the API spec:
- **Microservice management** — no endpoint exists
- **UI Customize** — no branding/theme API
- **ONVIF device discovery** — no search/discovery endpoint
- **Video recording settings** — no rule-based recording config API
- **Sync device operations** — no tenant-based sync endpoint
- **Task/Linkage edit form** — no task creation endpoint

---

## Part 2: API Specification Issues

### Critical (Block Integration)

| # | Issue | Affected Modules |
|---|-------|-----------------|
| 1 | Inconsistent status-update pattern — some use `PUT /:id/status`, others `PATCH /:id` | Users, Linkage Rules |
| 2 | Wrong HTTP status on create — `POST /devices`, `POST /data-sources`, `POST /device-groups/:id/devices` return `200` instead of `201` | 15+ endpoints |
| 3 | Missing bulk device operations — no `DELETE /devices` with body, no `PUT /devices/batch-update` | Device management |
| 4 | Inconsistent pagination — roles, menus, resources, regions, platforms, licenses return flat arrays instead of cursor envelope | 6 modules |
| 5 | Incomplete error schema — no field-level validation errors for 422 responses | All modules |

### Major (Degrade UX)

| # | Issue | Affected Modules |
|---|-------|-----------------|
| 6 | Missing `PATCH /devices/:id` — no lightweight update | Devices |
| 7 | Missing `PATCH /data-sources/:id` — no status toggle | Data Sources |
| 8 | Missing `PATCH /platforms/:id` — no enable/disable | Platforms |
| 9 | Missing `GET /resources/:id` — no resource detail view | Resources |
| 10 | Missing `GET /licenses/:id`, `PUT /licenses/:id` — no license detail/update | Licenses |
| 11 | Missing `PATCH /menus/:id` and `GET /menus/:id` — no menu detail or partial update | Menus |
| 12 | Missing `PATCH` on device-groups, regions, roles, algorithms, algorithm-services | 5 modules |
| 13 | No real-time endpoints — devices, algorithm-events, notifications use polling only | 3 modules |
| 14 | Missing password confirmation on admin password reset | Auth |
| 15 | Platform sync-status path naming inconsistency — `sync-status` vs `sync` | Platforms |

---

## Part 3: Database/API Gaps

### Critical (Block Integration)

| # | Issue | DB vs API |
|---|-------|-----------|
| 1 | `org` table missing `org_code` column — API requires it on create | DB lacks column API requires |
| 2 | `device` table missing `device_sn` and `device_port` columns — API sends on create | DB lacks columns |
| 3 | `refresh_token` table has no API exposure — no session list/revoke | No API endpoint exists |
| 4 | `deployment` and `deployment_annotation` tables have no API | No API endpoint exists |
| 5 | `device(region_id)` and `device(org_id)` have no FK constraints — orphaned devices risk | Schema integrity |

### Major (Cause Bugs)

| # | Issue | Impact |
|---|-------|--------|
| 6 | Status field type mismatch — DB SMALLINT, API sends strings (`"active"`) | Type coercion needed |
| 7 | `role.permissions` is JSONB but API sends `menu_ids`/`resource_ids` arrays — no junction tables | Schema/API mismatch |
| 8 | Memory/disk size format — DB bytes, API returns `"16G"` strings | Response parsing issue |
| 9 | `linkage_history` and `operation_log` partition indexes won't propagate | Performance degradation |
| 10 | No partition automation — inserts fail after 2026-12-31 | Production outage risk |
| 11 | `notification.recipients` JSONB array can't be indexed per-user | Query inefficiency |
| 12 | `deployment.target_ids` JSONB has no FK to device table | Orphaned IDs after deletion |

---

## Consolidated Gaps Requiring Action

### Must Fix Before Integration

1. **API**: Add `PATCH /resources/:id` and `GET /resources/:id` (CRITICAL for resource detail)
2. **API**: Add `PATCH /devices/:id`, `PATCH /data-sources/:id`, `PATCH /platforms/:id` for status toggles
3. **API**: Standardize all create endpoints to return `201 Created`
4. **API**: Add `GET /licenses/:id` and `PUT /licenses/:id` for license management
5. **DB**: Add `org_code VARCHAR(32)` to `org` table
6. **DB**: Add `device_sn VARCHAR(128)` and `device_port INTEGER` to `device` table
7. **DB/API**: Implement `/auth/sessions` endpoint for refresh token management
8. **DB/API**: Add `/deployments` CRUD module for deployment tracking

### Should Fix Within Sprint

9. **API**: Standardize list responses to cursor-paginated envelope (roles, menus, resources, regions, platforms, licenses)
10. **API**: Extend error schema with field-level validation errors
11. **API**: Add bulk device operations (`POST /devices/batch-delete`, `PUT /devices/batch-update`)
12. **DB**: Add FK constraints on `device(region_id)` and `device(org_id)`
13. **DB**: Add `UNIQUE(parent_id, name)` on `org`, `device_group`, `region`
14. **DB**: Implement automated partition creation for `linkage_history` and `operation_log`
15. **DB**: Add partitioned indexes on `linkage_history` and `operation_log`

### Nice to Have

16. **API**: Add WebSocket/SSE endpoints for real-time: devices, algorithm-events, notifications
17. **API**: Add bulk user import (CSV)
18. **API**: Add ONVIF device discovery endpoint
19. **API**: Add UI customize/branding endpoint
20. **API**: Document all JSONB field schemas in `docs/json-schemas/`

---

## Statistics Summary

| Layer | Critical | Major | Minor |
|-------|----------|-------|-------|
| Frontend (API integration) | 1 (all mock) | 0 | 0 |
| API Specification | 5 | 10 | 5 |
| Database Schema | 5 | 13 | 10 |
| API Coverage Gaps | 4 | 9 | 5 |
| **Total Unique Issues** | **~10** | **~20** | **~15** |

---

## Conclusion

The frontend is a pure mock prototype. No API integration exists. The API spec is 80% complete with consistent patterns but has significant gaps in PATCH coverage and status-update conventions. The database schema requires several column additions to match the API contract, plus structural fixes (FKs, partition automation). Integration work should proceed in priority order: (1) add missing DB columns, (2) fix API PATCH endpoints, (3) wire frontend to API service layer.
