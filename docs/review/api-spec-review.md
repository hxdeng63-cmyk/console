# REST API Specification Review Report

## Executive Summary

The AIoT Device Management Platform REST API demonstrates solid foundational design with consistent response envelopes, cursor-based pagination, and comprehensive CRUD coverage across 22 resource modules. However, several critical issues require attention before production: inconsistent status update patterns, ambiguous HTTP status code usage, missing bulk operations for device management, and incomplete error response schemas. The API would benefit from clearer resource relationship modeling and more explicit field-level documentation.

---

## Critical Issues

### 1. Inconsistent Status Update Patterns (High Priority)
**Severity:** Critical

Status updates use different HTTP methods across resources:
- `PUT /users/:id/status` (Section 3)
- `PUT /linkage-rules/:id/status` (Section 15)
- `PUT /auth/password` (Section 1)

**Problem:** Mixing `PUT` with nested resource paths (`/resource/:id/sub-resource`) for status changes is inconsistent with the rest of the API. Compare with:
- `POST /devices/:id/auth` for device authorization (action-based)

**Recommendation:** Standardize on either:
- Pattern A: `PATCH /resources/:id` with `{ "status": "disabled" }` (preferred, partial update semantics)
- Pattern B: `PUT /resources/:id/status` (nested resource pattern)

All status updates should follow the same pattern.

### 2. Ambiguous HTTP Status Code for Create Operations
**Severity:** Critical

Some endpoints return `200` for resource creation instead of `201 Created`:
- `POST /devices` returns `200` with `data: { id: 100 }` (line 791-796)
- `POST /data-sources` returns `200` (line 1220-1226)
- `POST /device-groups/:id/devices` returns `200` (line 1044-1055)

**Problem:** RESTful convention dictates `201 Created` for successful resource creation, with `Location` header pointing to the new resource. `200 OK` implies an operation that doesn't create a resource.

**Recommendation:** Change all create endpoints to return `201 Created` with the `Location` header set to the new resource URI.

### 3. Missing Bulk Device Operations
**Severity:** Critical

Device management lacks bulk update/delete:
- `DELETE /devices/:id` only deletes single device
- No bulk delete endpoint: `DELETE /devices` with body `{ device_ids: [...] }`
- No bulk update endpoint for batch operations

**Impact:** Frontend consumers must make N API calls for N devices, causing:
- Poor performance
- Race conditions on batch operations
- User experience degradation

**Recommendation:** Add:
- `POST /devices/batch-delete` with `{ device_ids: [...] }`
- `PUT /devices/batch-update` with `{ device_ids: [...], department: "..." }`

### 4. Platform Sync Status Endpoint Naming Inconsistency
**Severity:** Major

- `POST /platforms/:id/sync` (action endpoint)
- `GET /platforms/:id/sync-status` (status endpoint with hyphen)

**Problem:** Mixing snake_case (`sync_status`) with kebab-case inconsistently across the API.

**Recommendation:** Standardize on kebab-case for multi-word path segments: `GET /platforms/:id/sync-status` is correct. Ensure all path segments follow the same convention.

### 5. Incomplete Error Response Schema
**Severity:** Major

Error responses only include `code`, `message`, and `request_id`:
```json
{
  "code": <error_code>,
  "message": "<error_message>",
  "request_id": "req_abc123"
}
```

**Problems:**
- No field-level validation errors (critical for `422` responses)
- No `details` field for complex error context
- Frontend cannot highlight which fields failed validation

**Recommendation:** Extend error schema for validation errors:
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

---

## Major Issues

### 6. Missing Password Confirmation on Critical Operations
**Severity:** Major

- `PUT /auth/password` only requires `old_password` and `new_password`
- `PUT /users/:id/password` (admin resetting user password) requires only `{ password: "..." }` without confirmation

**Recommendation:** For admin password resets, require password confirmation field or re-authentication.

### 7. Inconsistent Pagination for Flat Lists
**Severity:** Major

Some endpoints return arrays directly instead of paginated objects:
- `GET /roles` returns `data: [...]` (array, line 477)
- `GET /menus` returns `data: [...]` (array, line 597)
- `GET /resources` returns `data: [...]` (array, line 679)
- `GET /regions` returns `data: [...]` (array, line 1092)
- `GET /platforms` returns `data: [...]` (array, line 1297)
- `GET /licenses` returns `data: [...]` (array, line 2091)

**Problem:** Inconsistent with cursor-based pagination pattern used elsewhere. Frontend must handle both array and paginated response formats.

**Recommendation:** Standardize all list endpoints to use cursor-based pagination envelope:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [...],
    "next_cursor": "...",
    "has_more": true
  }
}
```

### 8. Missing Required Query Parameters Documentation
**Severity:** Minor

- `GET /data-sources` requires `device_id` (line 1181) but it's not clearly marked as required
- `GET /algorithm-services` filters by `device_id` and `algorithm_id` but none are marked required

**Recommendation:** Clearly document which query parameters are required vs optional using OpenAPI `required` field.

### 9. No Rate Limiting Headers Documented
**Severity:** Minor

Error code `429 Rate Limited` is defined but no documentation of:
- Rate limit headers (e.g., `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`)
- Per-endpoint vs global rate limits

**Recommendation:** Document rate limit headers and thresholds.

### 10. Device Authorization Response Inconsistency
**Severity:** Minor

- `POST /devices/:id/auth` accepts `{ auth_code, auth_deadline }` (request body)
- `GET /devices/:id` shows `auth_status` and `auth_deadline` (read-only fields)

**Problem:** No endpoint to revoke authorization (set `auth_status: "unauthorized"`).

**Recommendation:** Add `DELETE /devices/:id/auth` or `PUT /devices/:id/auth` with `auth_status: "revoked"`.

---

## Minor Issues

### 11. Inconsistent Field Naming for Timestamps
**Severity:** Minor

- Most resources use `created_at` and `updated_at`
- Some responses include `last_login_at`, `last_heartbeat_at`, `triggered_at`, `occurred_at`, `completed_at`
- No consistency guideline for timestamp field naming

**Recommendation:** Establish naming convention:
- `*_at` for moment-in-time timestamps
- `*_by` for user references
- `*_count` for aggregations

### 12. Missing `updated_at` in Responses
**Severity:** Minor

- `GET /users/:id` does not include `updated_at`
- `POST /users` response only includes `{ id: 10 }`, not the created resource
- `PUT /users/:id` returns empty success, not updated resource

**Recommendation:** Return the updated resource on `PUT` operations for verification, or at minimum include `updated_at` in success response.

### 13. Device SN as UUID Format
**Severity:** Minor

- Device SN format: `2495eb13-a1b2-c3d4` (Section 7, line 754)
- This format may not be a valid UUID according to RFC 4122

**Recommendation:** Clarify SN format requirements or use UUID v4/v5 consistently.

### 14. Missing API Consumer Guidance
**Severity:** Minor

No documentation for:
- How to handle token refresh during active sessions
- Idempotency keys for create operations
- Webhook/notification callback setup
- SDK availability

**Recommendation:** Add a "Developer Guide" section covering common integration patterns.

---

## Endpoint-by-Endpoint Review

### Authentication (`/auth`) - Overall: Good

| Endpoint | Status | Notes |
|----------|--------|-------|
| `POST /auth/login` | OK | Standard login flow |
| `POST /auth/refresh` | OK | Token refresh pattern |
| `POST /auth/logout` | OK | |
| `GET /auth/me` | OK | Returns current user |
| `PUT /auth/password` | See Issue #1 | Inconsistent status update pattern |

### Organization (`/orgs`) - Overall: Good

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /orgs` | OK | Cursor pagination |
| `POST /orgs` | See Issue #2 | Should return 201 |
| `GET /orgs/:id` | OK | |
| `PUT /orgs/:id` | OK | |
| `DELETE /orgs/:id` | OK | 409 for children |
| `GET /orgs/:id/users` | OK | |
| `GET /orgs/tree` | OK | |

### User (`/users`) - Overall: Needs Work

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /users` | OK | |
| `POST /users` | See Issue #2 | Should return 201 |
| `GET /users/:id` | OK | |
| `PUT /users/:id` | OK | |
| `DELETE /users/:id` | OK | |
| `PUT /users/:id/password` | See Issue #6 | Missing confirmation |
| `PUT /users/:id/status` | See Issue #1 | Inconsistent pattern |
| `GET /users/:id/operations` | OK | |

### Role (`/roles`) - Overall: Needs Work

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /roles` | See Issue #7 | No pagination |
| `POST /roles` | See Issue #2 | Should return 201 |
| `GET /roles/:id` | OK | |
| `PUT /roles/:id` | OK | |
| `DELETE /roles/:id` | OK | 409 for assigned users |
| `GET /roles/:id/users` | OK | |

### Menu (`/menus`) - Overall: Needs Work

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /menus` | See Issue #7 | No pagination |
| `POST /menus` | See Issue #2 | Should return 201 |
| `PUT /menus/:id` | OK | |
| `DELETE /menus/:id` | OK | |

### Resource (`/resources`) - Overall: Needs Work

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /resources` | See Issue #7 | No pagination |
| `POST /resources` | See Issue #2 | Should return 201 |
| `PUT /resources/:id` | OK | |
| `DELETE /resources/:id` | OK | |

### Device (`/devices`) - Overall: Needs Work

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /devices` | OK | |
| `POST /devices` | See Issue #2, #3 | Should return 201, needs bulk ops |
| `GET /devices/:id` | OK | |
| `PUT /devices/:id` | OK | |
| `DELETE /devices/:id` | See Issue #3 | Needs bulk delete |
| `GET /devices/:id/stats` | OK | |
| `POST /devices/:id/auth` | OK | |
| `GET /devices/:id/video-sources` | OK | |
| `GET /devices/export` | OK | File download |

### Device Group (`/device-groups`) - Overall: Acceptable

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /device-groups` | OK | |
| `POST /device-groups` | See Issue #2 | Should return 201 |
| `GET /device-groups/:id` | OK | |
| `PUT /device-groups/:id` | OK | |
| `DELETE /device-groups/:id` | OK | |
| `GET /device-groups/:id/devices` | OK | |
| `POST /device-groups/:id/devices` | OK | |
| `DELETE /device-groups/:id/devices` | OK | |
| `GET /device-groups/tree` | OK | |

### Region (`/regions`) - Overall: Needs Work

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /regions` | See Issue #7 | No pagination |
| `POST /regions` | See Issue #2 | Should return 201 |
| `GET /regions/:id` | OK | |
| `PUT /regions/:id` | OK | |
| `DELETE /regions/:id` | OK | |
| `GET /regions/tree` | OK | |

### Data Source (`/data-sources`) - Overall: Acceptable

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /data-sources` | OK | |
| `POST /data-sources` | See Issue #2 | Should return 201 |
| `GET /data-sources/:id` | OK | |
| `PUT /data-sources/:id` | OK | |
| `DELETE /data-sources/:id` | OK | |
| `POST /data-sources/:id/test` | OK | Connectivity test |

### Platform (`/platforms`) - Overall: Needs Work

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /platforms` | See Issue #7 | No pagination |
| `POST /platforms` | See Issue #2 | Should return 201 |
| `GET /platforms/:id` | OK | |
| `PUT /platforms/:id` | OK | |
| `DELETE /platforms/:id` | OK | |
| `POST /platforms/:id/sync` | OK | |
| `GET /platforms/:id/sync-status` | See Issue #4 | Hyphen inconsistency |

### Algorithm (`/algorithms`) - Overall: Acceptable

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /algorithms` | OK | |
| `POST /algorithms` | See Issue #2 | Should return 201 |
| `GET /algorithms/:id` | OK | |
| `PUT /algorithms/:id` | OK | |
| `DELETE /algorithms/:id` | OK | |
| `POST /algorithms/:id/deploy` | OK | |

### Algorithm Service (`/algorithm-services`) - Overall: Acceptable

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /algorithm-services` | OK | |
| `POST /algorithm-services` | See Issue #2 | Should return 201 |
| `GET /algorithm-services/:id` | OK | |
| `PUT /algorithm-services/:id` | OK | |
| `DELETE /algorithm-services/:id` | OK | |
| `POST /algorithm-services/:id/start` | OK | |
| `POST /algorithm-services/:id/stop` | OK | |
| `GET /algorithm-services/:id/stats` | OK | |

### Algorithm Event (`/algorithm-events`) - Overall: Acceptable

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /algorithm-events` | OK | |
| `GET /algorithm-events/:id` | OK | |
| `PUT /algorithm-events/:id/handle` | OK | |
| `POST /algorithm-events/batch-handle` | OK | |
| `GET /algorithm-events/stats` | OK | |

### Linkage Rule (`/linkage-rules`) - Overall: Acceptable

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /linkage-rules` | OK | |
| `POST /linkage-rules` | See Issue #2 | Should return 201 |
| `GET /linkage-rules/:id` | OK | |
| `PUT /linkage-rules/:id` | OK | |
| `DELETE /linkage-rules/:id` | OK | |
| `POST /linkage-rules/:id/test` | OK | |
| `PUT /linkage-rules/:id/status` | See Issue #1 | Inconsistent pattern |

### Linkage History (`/linkage-histories`) - Overall: Acceptable

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /linkage-histories` | OK | |
| `GET /linkage-histories/:id` | OK | |

### Notification (`/notifications`) - Overall: Acceptable

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /notifications` | OK | |
| `PUT /notifications/:id/read` | OK | |
| `PUT /notifications/read-all` | OK | |
| `DELETE /notifications/:id` | OK | |

### License (`/licenses`) - Overall: Needs Work

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /licenses` | See Issue #7 | No pagination |
| `POST /licenses` | See Issue #2 | Should return 201 |
| `GET /licenses/verify` | OK | |
| `DELETE /licenses/:id` | OK | |

### Firmware (`/firmwares`) - Overall: Acceptable

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /firmwares` | OK | |
| `POST /firmwares` | See Issue #2 | Should return 201 |
| `GET /firmwares/:id` | OK | |
| `PUT /firmwares/:id` | OK | |
| `DELETE /firmwares/:id` | OK | |
| `POST /firmwares/:id/upgrade` | OK | |

### System Setting (`/system-settings`) - Overall: Needs Review

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /system-settings` | OK | |
| `PUT /system-settings` | OK | Batch update |
| `GET /system-settings/:key` | OK | |
| `PUT /system-settings/:key` | OK | |

**Note:** Having both batch (`PUT /system-settings`) and individual (`PUT /system-settings/:key`) update endpoints is confusing. Consider consolidating.

### Operation Log (`/operation-logs`) - Overall: Acceptable

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /operation-logs` | OK | |
| `GET /operation-logs/export` | OK | File export |

### File Manager (`/files`) - Overall: Acceptable

Endpoints appear complete for CRUD operations on file storage.

---

## Recommendations

### Immediate (Before Production)

1. **Standardize HTTP status codes**: Ensure all create operations return `201 Created`
2. **Fix status update pattern**: Choose `PATCH /resources/:id` or `PUT /resources/:id/status` and apply consistently
3. **Add bulk device operations**: Implement `POST /devices/batch-delete` and `PUT /devices/batch-update`
4. **Extend error schema**: Add field-level validation errors for `422` responses
5. **Standardize list responses**: Convert all flat array responses to cursor-paginated envelope

### Short Term (Post-MVP)

1. **Add rate limit headers** documentation
2. **Document required vs optional** query parameters
3. **Add `updated_at`** to user responses
4. **Standardize path naming**: Ensure kebab-case for all multi-word path segments
5. **Add device authorization revoke** endpoint

### Long Term (Platform Maturity)

1. **Create developer guide** with integration patterns
2. **Consider OpenAPI/Swagger** specification for automatic client generation
3. **Add idempotency keys** for create operations
4. **Implement webhook notifications** for async event processing
5. **Add SDK availability** documentation for common platforms

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Total Resource Modules | 22 |
| Total Endpoints | ~95 |
| Critical Issues | 5 |
| Major Issues | 4 |
| Minor Issues | 5 |
| Endpoints with 201 Issue | ~15 |
| Endpoints Missing Pagination | 6 |
| Endpoints with Inconsistent Status Pattern | 3 |
