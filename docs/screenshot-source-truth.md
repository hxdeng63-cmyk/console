# Screenshot Source of Truth

This document establishes ONE canonical reference screenshot per view to resolve conflicts when multiple screenshots exist for the same view.

## Rule

When 2+ screenshots exist for the same view, use the **NEWEST** screenshot as the authoritative source. Older screenshots are kept for historical context only.

---

## Super-admin Module

| View | Canonical Screenshot | Notes |
|------|---------------------|-------|
| Menu Management | `super-admin-menu-manage.png` | Reference for nested table with expandable rows |
| Resource Management | `super-admin-resource-manage.png` | Reference for HTTP method badges |
| Microservices | `super-admin-microservice.png` | Reference for service table |
| UI Customization | `super-admin-ui-customize.png` | Reference for theme color swatches |
| License File | `super-admin-license-file.png` | Reference for license status badges |

---

## User-center Module

| View | Canonical Screenshot | Notes |
|------|---------------------|-------|
| User Management | `user-center-user-manage.png` | Reference for avatar column |
| Organization Management | `user-center-org-manage.png` | Reference for tree with CRUD icons |
| Role Management | `user-center-role-manage.png` | Reference for role table |
| Operation History | `user-center-operation-history.png` | Reference for batch operations |

---

## Device Management Module

| View | Canonical Screenshot | Notes |
|------|---------------------|-------|
| Data Source | `device-data-source.png` | Reference for RTSP addresses and switches |
| Sync Device | `device-sync-device.png` | Reference for checkbox selection |
| Device | `device-device.png` | Reference for progress bars |
| Device Group | `device-device-group.png` | Generic CRUD reference |
| Region | `device-region.png` | Generic CRUD reference |
| Device Access - Platform List | `device-access-platform-list.png` | Reference for platform table |
| Device Access - GB28181 | `device-access-gb28181.png` | Reference for SIP config and nested tables |
| Device Access - ONVIF | `device-access-onvif.png` | Reference for ONVIF device search |

---

## Linkage Module

| View | Canonical Screenshot | Notes |
|------|---------------------|-------|
| Task Edit | `linkage-task-edit.png` | Reference for form layout |
| Linkage Rule | `linkage-rule.png` | Reference for status switches |
| Push History | `linkage-push-history.png` | Reference for status badges |

---

## System Settings Module

| View | Canonical Screenshot | Notes |
|------|---------------------|-------|
| Video Setting | `system-video-setting.png` | Reference for rule table |
| File Manager | `system-file-manager.png` | Reference for file type badges |
| Help Center | `help-center.png` | Reference for static content display |
| Popup Setting | `system-popup-setting.png` | Reference for switch controls |
| Dispose Tag | `system-dispose-tag.png` | Reference for tag table |

---

## Data Clean Module

| View | Canonical Screenshot | Notes |
|------|---------------------|-------|
| Data Clean | `data-clean.png` | Reference for radio group and progress table |

---

## Algorithm Management Module

| View | Canonical Screenshot | Notes |
|------|---------------------|-------|
| Algorithm Management | `algorithm-manage.png` | Reference for algorithm table |
| Event Management | `algorithm-event-manage.png` | Reference for event type/level badges |
| Algorithm Service | `algorithm-service.png` | Reference for JSON viewer |

---

## Firmware Center

| View | Canonical Screenshot | Notes |
|------|---------------------|-------|
| Firmware Center | `firmware-center.png` | Reference for firmware table |

---

## Upgrade Center

| View | Canonical Screenshot | Notes |
|------|---------------------|-------|
| Upgrade Center | `upgrade-center.png` | Reference for expandable sub-stats |

---

## Events/Warning Module

| View | Canonical Screenshot | Notes |
|------|---------------------|-------|
| Warning Events | `warning-events.png` | Reference for filter form + table + toggle |

---

## Layout Components

| Component | Canonical Screenshot | Notes |
|-----------|---------------------|-------|
| Sidebar | `layout-sidebar.png` | Reference for collapsed/expanded states |
| Header | `layout-header.png` | Reference for breadcrumb |
| Tabs | `layout-tabs.png` | Reference for tab bar |
| Login | `login.png` | Reference for login form |

---

## Conflict Resolution

If two screenshots of the same view show conflicting UI:

1. Compare timestamps (file modification date)
2. Use the **NEWER** screenshot as truth
3. Note the conflict in this document
4. Update this document after resolution

Example conflict record:
```
| View | Conflict | Resolution | Date |
|------|----------|------------|------|
| Device Data Source | `device-data-source-v1.png` vs `device-data-source.png` | v1 shows old switch style; use `device-data-source.png` | 2026-04-13 |
```
