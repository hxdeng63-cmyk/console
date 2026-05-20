# Cross-Review: DB Schema & API Specification Consistency

## Executive Summary

The database schema (24 tables) and API specification (24 modules) show strong structural alignment with 80% direct coverage. However, there are **3 critical gaps** (missing APIs for deployment/deployment_annotation, orphaned refresh_token table), **6 major field/type mismatches**, and **7 minor inconsistencies** that must be resolved before integration.

---

## Critical Gaps

### 1. `refresh_token` Table Has No API Exposure
- **Schema**: `refresh_token` table with fields `user_id`, `token_hash`, `device_info`, `ip`, `expires_at`, `revoked_at`
- **Issue**: No `/refresh-tokens` or `/auth/sessions` endpoint exists to list/revoke active sessions
- **Impact**: Users cannot view or revoke their active login sessions, violating security best practices
- **Recommendation**: Add `GET /auth/sessions` and `DELETE /auth/sessions/:id` endpoints

### 2. `deployment` and `deployment_annotation` Tables Have No API
- **Schema**: `deployment` table (status, progress, config, target_ids) and `deployment_annotation` table
- **Issue**: No `/deployments` API endpoint exists; algorithm deploy uses inline `device_ids` without persisting deployment records
- **Impact**: Deployment tracking and progress monitoring is not implemented server-side
- **Recommendation**: Add full `/deployments` CRUD module with `/deployments/:id/annotate` sub-endpoint

### 3. `device_group_member` Junction Table Has No Dedicated API
- **Schema**: `device_group_member` (device_id, group_id) is the junction table between device and device_group
- **Issue**: Only accessible via `GET /device-groups/:id/devices` as a sub-collection; no direct membership management endpoint
- **Impact**: Cannot add/remove devices from groups without going through group-level endpoints
- **Recommendation**: Consider if direct membership management is needed; current workaround is acceptable

---

## Major Gaps

### 4. Status Field Type Mismatch (String vs SmallInt)
- **Schema**: `status` is `SMALLINT NOT NULL DEFAULT 1` (0=disabled, 1=active)
- **API**: All status values sent as strings: `"active"`, `"disabled"`, `"online"`, `"offline"`
- **Impact**: Type coercion layer required; API contract does not reflect DB storage
- **Recommendation**: Standardize on SMALLINT with documented values, or document that API accepts string synonyms

### 5. `org` Table Missing `org_code` Column
- **Schema**: `org` has `name`, `parent_id`, `level`, `sort_order`, `status`
- **API**: `POST /orgs` requires `org_code` field; `GET /orgs` returns `org_code`
- **Impact**: CREATE org with `org_code` will fail; READ returns field not in schema
- **Recommendation**: Add `code VARCHAR(32) UNIQUE` column to `org` table, or remove from API

### 6. Role `menu_ids` and `resource_ids` Do Not Match Schema
- **Schema**: `role.permissions JSONB` (array of permission strings like `"user:read"`)
- **API**: `POST /roles` accepts `menu_ids: [1,2,3]` and `resource_ids: [101,102,103]`
- **Impact**: API assumes many-to-many role-menu and role-resource relationships that don't exist in schema
- **Recommendation**: Add `role_menu` and `role_resource` junction tables, or refactor API to use permissions JSONB

### 7. `device_sn` and `device_port` Not in Schema
- **API Request** (`POST /devices`): `device_sn: "test001-a1b2-c3d4"`, `device_port: 8000`
- **Schema**: `device` table has `device_name`, `device_ip` but NOT `device_sn` or `device_port`
- **Impact**: Device creation will fail if these fields are required; they may be silently ignored
- **Recommendation**: Add `device_sn VARCHAR(128)` and `device_port INTEGER` columns to `device` table

### 8. Memory/Disk Size Format Mismatch
- **Schema**: `memory_size BIGINT DEFAULT 0` (bytes as integer), `disk_size BIGINT DEFAULT 0`
- **API Response**: `"memory_size": "16G"`, `"disk_size": "256G"` (human-readable strings)
- **Impact**: API responses cannot be directly parsed as numbers; frontend must parse formatting
- **Recommendation**: Add computed columns `memory_size_fmt` and `disk_size_fmt` or document the format

### 9. `last_heartbeat` vs `last_heartbeat_at` Naming Inconsistency
- **Schema**: `last_heartbeat TIMESTAMPTZ`
- **API**: `last_heartbeat_at` (e.g., `"last_heartbeat_at": "2026-04-23T10:00:00Z"`)
- **Impact**: Minor naming inconsistency; no functional issue but adds confusion
- **Recommendation**: Align field names; prefer `last_heartbeat_at` as more descriptive

---

## Minor Gaps

### 10. `algorithm_service.service_address` is JSONB but API uses separate fields
- **Schema**: `service_address JSONB NOT NULL DEFAULT '[]'`
- **API**: Returns flattened fields `service_name`, `device_id`, `device_name`, `channel_configs`
- **Impact**: Service address JSONB structure is abstracted away; acceptable

### 11. `linkage_rule` conditions/actions vs API trigger_config/action_config
- **Schema**: `conditions JSONB`, `actions JSONB`
- **API**: `trigger_config`, `action_config` (nested wrapper)
- **Impact**: Field name translation required; not a functional issue
- **Recommendation**: Document mapping between schema field names and API field names

### 12. `users.last_login` vs API `last_login_at`
- **Schema**: `last_login TIMESTAMPTZ`
- **API**: `last_login_at` in user responses
- **Impact**: Field name inconsistency
- **Recommendation**: Use consistent naming

### 13. `users.gender` Not Exposed in API
- **Schema**: `gender SMALLINT DEFAULT 0`
- **API**: No gender field in user responses
- **Impact**: Data exists but is not exposed; may be intentional for privacy

### 14. `users.deleted_at` Soft Delete Not Reflected in API
- **Schema**: `deleted_at TIMESTAMPTZ` for soft delete
- **API**: `DELETE /users/:id` returns success but doesn't use soft delete semantics
- **Impact**: If API does hard delete but schema expects soft delete, data recovery is impossible
- **Recommendation**: Verify DELETE implementation uses soft delete

### 15. API `is_system` Boolean vs Schema `status` SmallInt
- **API Response** (`GET /roles/:id`): `"is_system": false` as boolean
- **Schema**: Role has `status SMALLINT` not `is_system` boolean
- **Impact**: Need derived field logic to compute `is_system` from role code
- **Recommendation**: Document that `is_system` is computed from `code = 'SUPER_ADMIN'`

### 16. Pagination Cursor Format
- **Schema**: No specific cursor column; uses `id BIGSERIAL`
- **API**: Cursor is base64 encoded `{"id":123}` format
- **Impact**: Must ensure cursor always includes `id` for correct pagination
- **Recommendation**: Document cursor structure and ensure indexed columns support cursor pagination

---

## Coverage Matrix

| Schema Table | API Module | Coverage Status | Notes |
|-------------|------------|-----------------|-------|
| org | `/orgs` | Full | Missing `code` column |
| role | `/roles` | Partial | Uses `menu_ids`/`resource_ids` not in schema |
| users | `/users` | Full | `last_login` vs `last_login_at` naming |
| device_group | `/device-groups` | Full | |
| device | `/devices` | Partial | Missing `device_sn`, `device_port` |
| device_group_member | `/device-groups/:id/devices` | Partial | Sub-collection only |
| region | `/regions` | Full | |
| data_source | `/data-sources` | Full | |
| algorithm | `/algorithms` | Full | |
| algorithm_event | `/algorithm-events` | Full | |
| algorithm_service | `/algorithm-services` | Full | |
| linkage_rule | `/linkage-rules` | Full | Field name mapping issue |
| linkage_history | `/linkage-histories` | Full | |
| notification | `/notifications` | Full | |
| menu | `/menus` | Full | |
| resource | `/resources` | Full | |
| license | `/licenses` | Full | |
| firmware | `/firmwares` | Full | |
| system_setting | `/system-settings` | Full | |
| operation_log | `/operation-logs` | Full | |
| refresh_token | — | **Missing** | No API for session management |
| deployment | — | **Missing** | No API for deployment tracking |
| deployment_annotation | — | **Missing** | No API |
| device_platform | `/platforms` | Partial | Only basic CRUD |

---

## Recommendations

### Priority 1 (Critical — Fix Before Integration)
1. Add `code VARCHAR(32)` to `org` table
2. Add `device_sn VARCHAR(128)` and `device_port INTEGER` to `device` table
3. Implement `/auth/sessions` endpoint for refresh token management
4. Add `/deployments` CRUD API module

### Priority 2 (Major — Fix Within Sprint)
5. Create `role_menu` and `role_resource` junction tables if role-menu-resource association is needed
6. Standardize status field representation (all SMALLINT or all VARCHAR, not mixed)
7. Add computed `memory_size_fmt` and `disk_size_fmt` columns or document string format

### Priority 3 (Minor — Fix in Next Iteration)
8. Rename `last_heartbeat` to `last_heartbeat_at` in schema for consistency
9. Add `is_system` computed column to role table
10. Document cursor pagination structure and indexed columns
11. Ensure all DELETE operations use soft delete (`deleted_at`) semantics

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 3 |
| Major | 6 |
| Minor | 7 |

**Overall Assessment**: Integration viable after Priority 1 fixes. The schema and API share a common architectural vision but have accumulated 16 inconsistencies during parallel development. Most are resolvable with column additions or field mapping documentation.