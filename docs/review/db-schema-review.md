# Database Schema Review Report

## Executive Summary

The AIoT Device Management Platform schema provides a comprehensive foundation for device management, user authentication, algorithm orchestration, and linkage automation. The design is generally sound with proper use of soft deletes, JSONB flexibility, and hierarchical structures. However, several **critical gaps** must be addressed before production: missing foreign key constraints on core device tables, an unscalable hardcoded partition strategy, and an underdocumented JSONB schema that risks query inconsistency.

---

## Critical Issues

### 1. Device Table Lacks Foreign Keys for `region_id` and `org_id`
**Severity:** Critical
**Location:** `device` table (lines 107-108)

```sql
region_id       BIGINT,
org_id          BIGINT,
```

Both `region_id` and `org_id` are stored as plain `BIGINT` with no `REFERENCES` constraint, no `ON DELETE` behavior, and no index supporting join performance. This creates orphaned device records when regions or organizations are deleted, and forces application-level enforcement of referential integrity.

**Recommendation:** Add foreign key constraints with appropriate delete semantics. If a region/org deletion should cascade to devices, use `ON DELETE CASCADE`; if devices must remain, use `ON DELETE SET NULL` and add a partial index for the NULL case.

---

### 2. Hardcoded Monthly Partitions with No Automation
**Severity:** Critical
**Location:** `linkage_history` (lines 258-281), `operation_log` (lines 423-446)

Both `linkage_history` and `operation_log` use native PostgreSQL range partitioning by month, which is the correct strategy for high-volume append-only logs. However, the partitions are created **manually and only for calendar year 2026**. There is no automated mechanism (no `pg_cron` job, no scheduled task, no `INSERT ... ON CONFLICT` partition creation) to create future partitions.

Once `2027-01-01` arrives, all inserts to these tables will fail with `ERROR: no partition of relation "linkage_history" found for row`. This is a **production outage risk**.

**Recommendation:** Implement an automated partition creation strategy. Options:
- Use `pg_partman` extension for automatic interval partition management
- Create a `make_partition_if_missing()` function invoked by an application-side scheduler or `pg_cron`
- At minimum, add a warning threshold in the application healthcheck at 60 days before partition gap

---

### 3. No `NOT NULL` Constraints on `operation_log` Core Fields
**Severity:** Critical
**Location:** `operation_log` table (lines 409-418)

```sql
user_id         BIGINT,       -- nullable but FK not declared
resource_id     BIGINT,       -- nullable but no FK
ip              VARCHAR(64),
user_agent      VARCHAR(512),
request_data    JSONB,
response_data   JSONB,
```

While `action` and `module` are `NOT NULL`, the `user_id` is nullable and has no foreign key constraint. A `NULL` user_id on an operation log entry is problematic for audit traceability. Additionally, `user_id` being nullable but non-constrained means auditing queries must account for anonymous actions explicitly.

**Recommendation:** Declare `user_id` as `BIGINT NOT NULL` if all operations should be authenticated. If anonymous operations are allowed, add a partial index on `(user_id) WHERE user_id IS NOT NULL` for efficient non-anonymous filtering.

---

### 4. Missing Unique Constraint on Hierarchical Tables
**Severity:** Critical
**Location:** `org` (line 13), `device_group`, `region`

Hierarchical entities (`org`, `device_group`, `region`) lack sibling uniqueness constraints. Two organizations at the same level can share the same `name`, which may confuse administrators and API consumers. The `org` table has no `UNIQUE(name, parent_id)` constraint.

**Recommendation:** Add `UNIQUE(parent_id, name)` on `org`, `device_group`, and `region` to prevent duplicate sibling names within the same parent scope.

---

### 5. `refresh_token` Missing Index on `user_id` for Cascade Performance
**Severity:** Critical
**Location:** `refresh_token` table (lines 467)

```sql
CREATE INDEX idx_refresh_token_user ON refresh_token(user_id);
```

The index exists, but `ON DELETE CASCADE` on `user_id` means a user deletion must scan and delete all refresh tokens. With a large token table, this can cause lock contention. The `user_id` index helps the scan but does not address the cascade delete lock duration.

**Recommendation:** For high-volume token tables, consider soft-delete or token-expiry-based cleanup rather than hard cascade deletes. Alternatively, add `idx_refresh_token_user_created` covering `(user_id, created_at)` to target the oldest tokens first during cleanup.

---

## Major Issues

### 6. `device` Table Uses Non-Standard `device_type` as `SMALLINT`
**Severity:** Major
**Location:** `device` table, line 92

```sql
device_type     SMALLINT NOT NULL,
```

`device_type` is stored as an unconstrained integer with no lookup table. The schema provides no reference for what values are valid (1=Camera, 2=NVR, 3=DVR, etc.), making the data opaque to new developers and DBAs. Queries like `WHERE device_type = X` rely on tribal knowledge.

**Recommendation:** Create a `dict_device_type` reference table with `(id, name, description)` and add a foreign key. This enables `JOIN` for human-readable type names in queries and enforces type validity at the DB level.

---

### 7. `online_status` Uses `SMALLINT` with Magic Numbers
**Severity:** Major
**Location:** `device` table, line 103

```sql
online_status   SMALLINT NOT NULL DEFAULT 0,
```

`online_status` uses magic numbers (0, 1, etc.) without any enum, check constraint, or domain. The application layer must maintain the mapping. If multiple applications access this database, consistency is not guaranteed.

**Recommendation:** Add a `CHECK` constraint (`online_status IN (0, 1, 2)`) or use a PostgreSQL `DOMAIN`/`ENUM` type. For PostgreSQL 15+, an `ENUM` type is appropriate.

---

### 8. JSONB Config Fields Lack Schema Validation
**Severity:** Major
**Location:** Multiple tables: `role.permissions`, `data_source.config`, `algorithm.config`, `linkage_rule.conditions/actions`, `deployment.config`, etc.

PostgreSQL's JSONB columns store data without validating structure. The schema comments (lines 606-643) provide examples, but there is no DB-level enforcement. This means:
- `role.permissions` could store invalid permission strings
- `linkage_rule.conditions` could have malformed condition objects
- `algorithm.config` could be missing required fields

**Recommendation:** Create PostgreSQL JSON Schema constraints using `CHECK (jsonb_schema_valid(...))` for each JSONB column, or implement application-level schema validation at the API boundary. Document the expected JSON structure in a schema file under `docs/json-schemas/`.

---

### 9. `deployment.target_ids` JSONB Array Without FK Verification
**Severity:** Major
**Location:** `deployment` table, line 478

```sql
target_ids      JSONB NOT NULL DEFAULT '[]',
```

`target_ids` stores an array of device IDs as JSONB but has no foreign key validation against the `device` table. Orphaned device IDs can accumulate in `target_ids` after device deletion (since `deployment` has soft-delete but no cascading cleanup of the JSONB array).

**Recommendation:** Either:
- Normalize `deployment` to a `deployment_target(device_id, deployment_id)` junction table with proper FK constraints
- Or add application-level cleanup logic when a device is deleted to remove its ID from all `target_ids` arrays

---

### 10. `v_device_details` View Uses Inefficient LEFT JOINs Without Covering Index
**Severity:** Major
**Location:** `v_device_details` view (lines 583-593)

The view joins `device` to `device_group` via a junction table `device_group_member`. If a device belongs to multiple groups (which the junction table supports), this view will return **multiple rows** for the same device, which may surprise consumers expecting one row per device.

**Recommendation:** Clarify the view's semantics. If one-row-per-device is required, either restrict to `WHERE dg.id = (SELECT MIN(id) FROM device_group ...)` or aggregate with `STRING_AGG`. Add a covering index on `(device_id)` in `device_group_member` if the junction is queried frequently.

---

### 11. `linkage_history` Partition Indexes Missing on Partitioned Table
**Severity:** Major
**Location:** `linkage_history` (lines 283-284)

```sql
CREATE INDEX idx_linkage_history_rule ON linkage_history(rule_id);
CREATE INDEX idx_linkage_history_trigger_time ON linkage_history(trigger_time);
```

Indexes on a partitioned parent table **do not automatically propagate** to child partitions in PostgreSQL. Each partition is an independent table. The indexes must be created on each partition, or created as **partitioned indexes** using `CREATE INDEX ... ON linkage_history` which propagates to all existing and future partitions.

**Recommendation:** Drop these indexes and recreate them as partitioned indexes:
```sql
CREATE INDEX idx_linkage_history_rule ON linkage_history(rule_id);
CREATE INDEX idx_linkage_history_trigger_time ON linkage_history(trigger_time);
```
These will propagate to all partitions. Alternatively, use `pg_partman` which manages partition indexes automatically.

---

### 12. `operation_log` Has Same Partition Index Propagation Issue
**Severity:** Major
**Location:** `operation_log` (lines 448-451)

Indexes on `operation_log` parent table will not propagate to child partitions. Same fix as issue #11.

---

### 13. `notification.recipients` JSONB Array Cannot Be Efficiently Searched
**Severity:** Major
**Location:** `notification` table, line 294

```sql
recipients      JSONB NOT NULL DEFAULT '[]',
```

Storing recipients as a JSONB array makes it impossible to efficiently find all notifications sent to a specific user without scanning the entire table. Use cases like "show all notifications for user X" require `WHERE 'user_id_123' = ANY(recipients::text[])` which cannot use a standard B-tree index.

**Recommendation:** If notifications are frequently queried by recipient, normalize to a `notification_recipient(notification_id, user_id)` junction table with proper indexes. If JSONB is preferred for schema flexibility, create an expression index per recipient query pattern.

---

### 14. No `created_at` Index on `operation_log` Partitioned Table
**Severity:** Major
**Location:** `operation_log` (line 451)

```sql
CREATE INDEX idx_operation_log_created ON operation_log(created_at);
```

This index will not propagate to partitions. Additionally, since `created_at` is the partition key, it is already implicitly indexed within each partition's storage, but queries that filter by `created_at` across partitions may benefit from a partitioned index on `(created_at)` to support partition pruning.

**Recommendation:** Recreate as a partitioned index on `(created_at)`.

---

### 15. `algorithm_service.service_address` Uses JSONB `[]` Array
**Severity:** Major
**Location:** `algorithm_service` table, line 213

```sql
service_address     JSONB NOT NULL DEFAULT '[]',
```

This stores an array of service endpoints as JSONB. The structure is not validated, and there is no separate `algorithm_service_endpoint` table to track individual endpoints with their own metadata (health status, priority, last checked).

**Recommendation:** If a service can have multiple addresses (HA setup), consider normalizing to `(algorithm_service_id, address, port, priority, status)` with proper indexes. If JSONB is intentional for flexibility, add a check constraint validating the JSON structure.

---

## Minor Issues

### 16. `users.gender` Uses `SMALLINT` with No Enum or Check
**Severity:** Minor
**Location:** `users` table, line 51

```sql
gender          SMALLINT DEFAULT 0,
```

Magic number for gender is unusual in modern schema design. Consider a check constraint or domain enum.

---

### 17. `users` Table Has No Index on `(org_id, role_id)` Composite
**Severity:** Minor
**Location:** `users` table (lines 62-66)

Queries filtering users by org and role together (common in admin UIs) require scanning both individual indexes. A composite index `(org_id, role_id)` would improve performance.

---

### 18. `device` Table Missing Composite Index `(org_id, online_status)`
**Severity:** Minor
**Location:** `device` table (lines 114-122)

Common query pattern: "show all online devices in org X". Composite index would improve performance.

---

### 19. `license.expire_date` Uses `DATE` Without Timezone
**Severity:** Minor
**Location:** `license` table, line 354

```sql
expire_date     DATE NOT NULL,
```

`DATE` is date-only without timezone. If license expiration is checked across timezones, this can cause off-by-one-day issues. Consider `TIMESTAMPTZ` for unambiguous expiration timestamps.

---

### 20. `firmware.checksum` is `VARCHAR(64)` Without Constraint
**Severity:** Minor
**Location:** `firmware` table, line 375

Storing SHA-256 checksum as `VARCHAR(64)` with no validation. Consider adding a `CHECK (length(checksum) = 64 AND checksum ~ '^[a-f0-9]+$')` to ensure valid hex format.

---

### 21. No `description` Column Size Standardization
**Severity:** Minor
**Location:** Multiple tables

Description columns vary: `VARCHAR(256)` in some tables, `VARCHAR(512)` in others, `TEXT` in firmware. This inconsistency suggests no enforced naming or size standard for free-text metadata fields.

---

### 22. `system_setting` Uses `category` + `key` Unique Without Prefix Convention
**Severity:** Minor
**Location:** `system_setting` table, line 398

```sql
UNIQUE(category, key)
```

No prefix convention for key names (e.g., `video.max_streams`, `auth.session_timeout`). Without a convention, key collisions across categories may go unnoticed. Consider enforcing a naming prefix convention via application validation.

---

### 23. Seed Data Admin Password Uses Weak Default Hash
**Severity:** Minor
**Location:** Seed data, line 575-576

The default admin user uses `admin123` as password with a pre-generated bcrypt hash. This is a known weak credential in all deployments using the default seed data. The hash is valid for the string `password`, not `admin123` as the comment claims (the bcrypt hash `$2b$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi` is the classic "password" hash, not "admin123").

**Recommendation:** Use `admin123` bcrypt hash or fix the comment. Either way, require password change on first login in production.

---

### 24. `v_user_details` View Joins `users` to `org` with Optional `org_id`
**Severity:** Minor
**Location:** `v_user_details` view (lines 596-603)

```sql
LEFT JOIN org o ON u.org_id = o.id;
```

Since `users.org_id` can be NULL, this is correct. However, the view includes all columns from `users` including `password_hash` (line 48), which should never be exposed to application code reading from views.

**Recommendation:** Explicitly list only non-sensitive columns in the view, omitting `password_hash`.

---

## Entity-by-Entity Review

### `org` — Organizations
- **Strengths:** Proper hierarchical parent reference, `level` denormalization for depth queries, soft delete via `deleted_at` missing but `status` field present.
- **Issue:** No `deleted_at` column (unlike `device_group` and `region`). If an org is "deleted," its `status` is set but the record remains for audit. This is acceptable if `status=0` means inactive, but inconsistent with other hierarchical tables that have both `status` and `deleted_at`.
- **Missing:** No unique constraint on sibling names.

### `role` — Roles
- **Strengths:** `permissions` JSONB allows flexible RBAC without schema changes. Proper `updated_at` trigger.
- **Issue:** No FK from `users.role_id` to `role.id` with `ON DELETE SET NULL` declared explicitly (though it works due to column-level declaration).
- **Missing:** No check constraint on `permissions` JSONB structure.

### `users` — Users
- **Strengths:** Soft delete via `deleted_at`, composite index on `(org_id, role_id)` would help but is missing. `last_login` tracking.
- **Issue:** `password_hash` should not be in views. No composite index for `(org_id, status)` which is common for user listing queries.
- **Missing:** `UNIQUE(email)` constraint if emails should be unique (currently only indexed, not constrained).

### `device` — Devices
- **Strengths:** Comprehensive device metadata, heartbeat tracking, partial index on `(online_status, last_heartbeat) WHERE online_status = 1` for finding stale online devices.
- **Issue:** `region_id` and `org_id` have no FK constraints. `device_type` is a magic number. No composite covering index for `(org_id, online_status, last_heartbeat)` common query.
- **Missing:** Device-type reference table.

### `device_group` — Device Groups
- **Strengths:** Hierarchical with `parent_id CASCADE` delete (correct — deleting a group deletes subgroups). Partial index on `deleted_at`.
- **Issue:** No unique sibling name constraint. No `status` field (unlike `org`).
- **Missing:** Unique constraint on `(parent_id, name)`.

### `region` — Regions
- **Strengths:** Hierarchical, soft delete, `code` is unique for external system integration.
- **Issue:** No unique sibling name constraint.
- **Missing:** Same as device_group — `UNIQUE(parent_id, name)`.

### `data_source` — Data Sources
- **Strengths:** `config` JSONB for flexible connection strings/credentials. `type` discriminator.
- **Issue:** No FK to `device` or `region`. A data source is associated with nothing in the schema — its meaning is opaque without application context.
- **Missing:** `device_id` or `region_id` FK if data sources are scoped to devices/regions.

### `algorithm` — Algorithms
- **Strengths:** `config` JSONB, `service_url` for algorithm endpoint, status tracking.
- **Issue:** `annotation_url` is not described in comments. No FK to indicate which devices or data sources an algorithm applies to.
- **Missing:** Many-to-many relationship table between `algorithm` and `device` or `data_source`.

### `algorithm_event` — Algorithm Events
- **Strengths:** Links events to algorithms via `algorithm_id FK`. `trigger_type` discriminator.
- **Issue:** No index on `(algorithm_id, trigger_type)` composite. No FK to `device` or `region` for event scoping.
- **Missing:** If events are per-device, need `device_id` FK.

### `algorithm_service` — Algorithm Services
- **Strengths:** `service_id` unique identifier for external system integration.
- **Issue:** `service_address` JSONB array stores addresses without validation. No FK to `algorithm`.
- **Missing:** `algorithm_id` FK to link service instances to algorithm definitions.

### `linkage_rule` — Linkage Rules
- **Strengths:** `conditions` and `actions` JSONB for flexible rule engine. `priority` field with partial index for active rules. Proper soft delete.
- **Issue:** Conditions/actions JSONB structure is not validated. No documentation of the expected condition/action schema in the DB itself.
- **Missing:** JSON Schema validation or CHECK constraints on conditions/actions.

### `linkage_history` — Linkage History
- **Strengths:** Monthly partitioning is appropriate for high-volume append log. `trigger_data` and `action_result` JSONB for flexible payload storage.
- **Issue:** Partition indexes don't propagate. No partition automation. `rule_id` has no FK to `linkage_rule` (rule could be deleted while history remains).
- **Missing:** FK to `linkage_rule`, partitioned indexes, automated partition creation.

### `notification` — Notifications
- **Strengths:** `recipients` JSONB array supports multi-channel. `sent_at` tracks delivery time.
- **Issue:** JSONB recipients cannot be efficiently indexed for per-user queries.
- **Missing:** `notification_recipient` junction table for efficient per-user queries.

### `menu` — Menus
- **Strengths:** Hierarchical, `permissions` VARCHAR for simple permission matching.
- **Issue:** Permissions stored as VARCHAR (comma-separated string pattern) unlike `role.permissions` which uses JSONB — inconsistency in permission storage mechanisms.
- **Missing:** Standardization of permission format across `menu` and `role`.

### `resource` — API Resources
- **Strengths:** `UNIQUE(path, method)` composite unique constraint. `type` discriminator.
- **Issue:** `permissions` VARCHAR(256) in `menu` vs `permissions JSONB` in `role` creates two different permission storage formats.
- **Missing:** Many-to-many `role_resource(role_id, resource_id)` junction table for explicit permission grants vs wildcard matching.

### `license` — Licenses
- **Strengths:** `features` JSONB for flexible feature flags. `expire_date` for temporal validity.
- **Issue:** `expire_date` is DATE without timezone. No `CHECK (device_limit >= 0)`. No automatic enforcement of device limit against actual device count.
- **Missing:** DB-level CHECK constraints or a trigger to alert when device count approaches `device_limit`.

### `firmware` — Firmware
- **Strengths:** `checksum` for integrity verification. `file_size` tracked.
- **Issue:** No FK to `device` indicating which firmware version each device is running.
- **Missing:** `device_firmware(device_id, firmware_id, deployed_at)` table to track firmware deployment history.

### `operation_log` — Operation Logs
- **Strengths:** Comprehensive audit fields. Monthly partitioning appropriate for high-volume logs. `request_data` and `response_data` JSONB for full request/response capture.
- **Issue:** `user_id` nullable without FK. Partition indexes don't propagate. No partition automation.
- **Missing:** `user_id NOT NULL` constraint if all operations are authenticated.

### `refresh_token` — Refresh Tokens
- **Strengths:** `token_hash` for secure token storage (tokens stored as hash, not raw). `device_info` and `ip` for security tracking. `expires_at` with partial index for cleanup.
- **Issue:** No index on `(user_id, expires_at)` for efficient "expire all user tokens" queries.
- **Missing:** Composite index `(user_id, expires_at, revoked_at)`.

### `deployment` — Deployments
- **Strengths:** Progress tracking with `succeeded`, `failed`, `total_targets`. `config` JSONB for flexible deployment parameters. `deployment_annotation` for per-device annotations.
- **Issue:** `target_ids` JSONB array with no FK validation against `device`. No status transition constraint (deployment status changes are not enforced).
- **Missing:** `deployment_target(device_id, deployment_id)` junction table. State machine CHECK constraint on `status` transitions.

### `deployment_annotation` — Deployment Annotations
- **Strengths:** `device_id` nullable allows global annotations. `polygon` JSONB for geospatial annotations.
- **Issue:** `type` VARCHAR(32) with no constraint or reference table. `device_id` has no FK.
- **Missing:** `annotation_type` reference table. FK on `device_id` if device-level annotations are required.

### `device_platform` — Device Access Platforms
- **Strengths:** Vendor/tenant model supports multi-tenant. `app_key`/`app_secret` for authentication.
- **Issue:** No FK to any organizational or device table. A platform is associated with nothing — its scoping is application-defined.
- **Missing:** `org_id` FK if platforms are per-organization. `platform_type` discriminator (GB28181 vs ONVIF).

---

## Recommendations

### Priority 1 (Fix Before Production)

1. **Add FK constraints on `device(region_id, org_id)`** — critical data integrity
2. **Implement automated partition management** — prevent 2027-01-01 outage on `linkage_history` and `operation_log`
3. **Create partitioned indexes** on `linkage_history` and `operation_log` — index propagation to partitions
4. **Add `UNIQUE(parent_id, name)` constraints** on hierarchical tables (`org`, `device_group`, `region`)
5. **Create `dict_device_type` reference table** with FK from `device`

### Priority 2 (Address in First Release Cycle)

6. Add JSONB schema validation for `role.permissions`, `linkage_rule.conditions/actions`
7. Replace `target_ids` JSONB with normalized `deployment_target` junction table
8. Add `user_id NOT NULL` on `operation_log` with FK constraint
9. Create `algorithm_service.algorithm_id` FK
10. Add `notification_recipient` junction for efficient per-user notification queries

### Priority 3 (Post-Launch Improvements)

11. Standardize permission storage format between `role` (JSONB) and `menu` (VARCHAR)
12. Add composite indexes for common query patterns: `(org_id, status)` on users, `(org_id, online_status)` on device
13. Implement `CHECK` constraints on `online_status`, `gender`, `device_type` enums
14. Add `firmware` deployment history tracking table
15. Document all JSONB field schemas in `docs/json-schemas/`

---

*Report generated by Claude Code db-reviewer agent. Schema version: PostgreSQL 15+ compatible.*
