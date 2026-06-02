# AI Console 数据库文档

> 生成时间: 2026-06-01

---

# 一、表关系总览

## 1.1 外键关系图

```
annotation.deployment_id -> deployment.id
annotation.device_id -> device.id
data_source.region_id -> region.id
data_source.device_id -> device.id
data_source.org_id -> organization.id
deployment.algorithm_id -> algorithm.id
deployment.service_id -> algorithm_service.id
deployment_device.device_id -> device.id
deployment_device.deployment_id -> deployment.id
deployment_schedule.deployment_id -> deployment.id
device.org_id -> organization.id
device.region_id -> region.id
device_stream.device_id -> device.id
event_type.algorithm_id -> algorithm.id
event_type_pt_weight.pt_weight_file_id -> pt_weight_file.id
event_type_pt_weight.event_type_id -> event_type.id
file.warning_event_id -> warning_event.id
file.device_id -> device.id
gb28181_device.device_id -> device.id
linkage_rule.algorithm_id -> algorithm.id
linkage_rule.event_type_id -> event_type.id
linkage_rule_device.device_id -> device.id
linkage_rule_device.linkage_rule_id -> linkage_rule.id
menu.parent_id -> menu.id
onvif_device.device_id -> device.id
organization.parent_id -> organization.id
preset.device_id -> device.id
push_history.device_id -> device.id
push_history.rule_id -> linkage_rule.id
push_history.event_type_id -> event_type.id
region.org_id -> organization.id
region.parent_id -> region.id
role_menu.role_id -> role.id
role_menu.menu_id -> menu.id
role_resource.resource_id -> resource.id
role_resource.role_id -> role.id
task.algorithm_id -> algorithm.id
task_device.task_id -> task.id
task_device.device_id -> device.id
user.org_id -> organization.id
user_role.role_id -> role.id
user_role.user_id -> user.id
video_setting.org_id -> organization.id
warning_event.rule_id -> linkage_rule.id
warning_event.event_type_id -> event_type.id
warning_event.algorithm_id -> algorithm.id
warning_event.region_id -> region.id
warning_event.org_id -> organization.id
warning_event.device_id -> device.id
warning_event_tag.warning_event_id -> warning_event.id
warning_event_tag.dispose_tag_id -> dispose_tag.id
```

## 1.2 模块划分

### 组织与用户

- `organization`
- `user`
- `user_role`
- `role`
- `role_menu`
- `role_resource`
- `menu`
- `resource`

### 设备管理

- `device`
- `region`
- `device_stream`
- `preset`
- `gb28181_device`
- `onvif_device`
- `video_setting`

### 算法与任务

- `algorithm`
- `algorithm_service`
- `pt_weight_file`
- `event_type`
- `event_type_pt_weight`
- `task`
- `task_device`
- `deployment`
- `deployment_device`
- `deployment_schedule`
- `annotation`

### 预警事件

- `warning_event`
- `warning_event_tag`
- `warning_event_archive`
- `dispose_tag`
- `event_type`
- `popup_event_limit`
- `popup_setting`
- `file`

### 联动规则

- `linkage_rule`
- `linkage_rule_device`
- `push_history`

### 数据与清理

- `data_source`
- `clean_record`

### 固件与许可

- `firmware`
- `license`
- `access_platform`
- `microservice`
- `ui_theme`

### 操作日志

- `operation_log`

---

# 二、表结构及数据详情

## access_platform

**主键**: `id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| name | character varying | NO |  |
| type | character varying | NO |  |
| version | character varying | YES |  |
| device_count | integer | NO |  |
| status | character varying | NO |  |
| config_json | jsonb | NO |  |
| id | bigint | NO | nextval('access_platform_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (15 条)

| name | type | version | device_count | status | config_json | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RTSP平台-01 | RTSP | v2.4 | 25 | active | {'transport': 'tcp', 'buffer_size': 4096} | 1 | 2026-05-31 21:29:06.102556+00:00 | 2026-05-31 21:29:06.102562+00:00 | NULL | NULL | NULL |
| RTSP平台-02 | RTSP | v5.1 | 0 | active | {'transport': 'tcp', 'buffer_size': 4096} | 2 | 2026-05-31 21:29:06.102565+00:00 | 2026-05-31 21:29:06.102568+00:00 | NULL | NULL | NULL |
| ONVIF平台-03 | ONVIF | v5.6 | 4 | active | {'probe_interval': 30, 'discovery_timeout': 5} | 3 | 2026-05-31 21:29:06.102570+00:00 | 2026-05-31 21:29:06.102572+00:00 | NULL | NULL | NULL |
| RTSP平台-04 | RTSP | v4.1 | 36 | inactive | {'transport': 'tcp', 'buffer_size': 4096} | 4 | 2026-05-31 21:29:06.102575+00:00 | 2026-05-31 21:29:06.102577+00:00 | NULL | NULL | NULL |
| RTMP平台-05 | RTMP | v4.9 | 11 | active | {'app': 'live', 'stream_timeout': 60} | 5 | 2026-05-31 21:29:06.102580+00:00 | 2026-05-31 21:29:06.102582+00:00 | NULL | NULL | NULL |
| GB28181平台-06 | GB28181 | v4.4 | 17 | active | {'sip_domain': '3402000000', 'sip_server_id': '... | 6 | 2026-05-31 21:29:06.102584+00:00 | 2026-05-31 21:29:06.102587+00:00 | NULL | NULL | NULL |
| RTMP平台-07 | RTMP | v5.8 | 3 | active | {'app': 'live', 'stream_timeout': 60} | 7 | 2026-05-31 21:29:06.102589+00:00 | 2026-05-31 21:29:06.102592+00:00 | NULL | NULL | NULL |
| GB28181平台-08 | GB28181 | v2.6 | 33 | active | {'sip_domain': '3402000000', 'sip_server_id': '... | 8 | 2026-05-31 21:29:06.102594+00:00 | 2026-05-31 21:29:06.102596+00:00 | NULL | NULL | NULL |
| GB28181平台-09 | GB28181 | v1.6 | 26 | active | {'sip_domain': '3402000000', 'sip_server_id': '... | 9 | 2026-05-31 21:29:06.102599+00:00 | 2026-05-31 21:29:06.102601+00:00 | NULL | NULL | NULL |
| RTSP平台-10 | RTSP | v2.8 | 10 | active | {'transport': 'tcp', 'buffer_size': 4096} | 10 | 2026-05-31 21:29:06.102604+00:00 | 2026-05-31 21:29:06.102606+00:00 | NULL | NULL | NULL |
| RTMP平台-11 | RTMP | v1.0 | 43 | inactive | {'app': 'live', 'stream_timeout': 60} | 11 | 2026-05-31 21:29:06.102608+00:00 | 2026-05-31 21:29:06.102611+00:00 | NULL | NULL | NULL |
| ONVIF平台-12 | ONVIF | v5.8 | 47 | active | {'probe_interval': 30, 'discovery_timeout': 5} | 12 | 2026-05-31 21:29:06.102613+00:00 | 2026-05-31 21:29:06.102615+00:00 | NULL | NULL | NULL |
| GB28181平台-13 | GB28181 | v5.0 | 44 | inactive | {'sip_domain': '3402000000', 'sip_server_id': '... | 13 | 2026-05-31 21:29:06.102618+00:00 | 2026-05-31 21:29:06.102620+00:00 | NULL | NULL | NULL |
| ONVIF平台-14 | ONVIF | v1.4 | 3 | active | {'probe_interval': 30, 'discovery_timeout': 5} | 14 | 2026-05-31 21:29:06.102623+00:00 | 2026-05-31 21:29:06.102625+00:00 | NULL | NULL | NULL |
| ONVIF平台-15 | ONVIF | v3.8 | 6 | active | {'probe_interval': 30, 'discovery_timeout': 5} | 15 | 2026-05-31 21:29:06.102627+00:00 | 2026-05-31 21:29:06.102630+00:00 | NULL | NULL | NULL |

---

## algorithm

**主键**: `id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| name | character varying | NO |  |
| type | character varying | YES |  |
| description | character varying | YES |  |
| business_category | character varying | YES |  |
| id | bigint | NO | nextval('algorithm_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (1 条)

| name | type | description | business_category | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 交通算法 | detection | 交通事件检测与流量统计 | 交通 | 1 | 2026-05-31 21:29:06.113049+00:00 | 2026-05-31 21:29:06.113055+00:00 | NULL | NULL | NULL |

---

## algorithm_service

**主键**: `id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| service_id | character varying | YES |  |
| service_name | character varying | YES |  |
| service_code | character varying | YES |  |
| service_ip | character varying | YES |  |
| service_port | integer | YES |  |
| annotation_ip | character varying | YES |  |
| annotation_port | integer | YES |  |
| status | character varying | NO |  |
| id | bigint | NO | nextval('algorithm_service_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (12 条)

| service_id | service_name | service_code | service_ip | service_port | annotation_ip | annotation_port | status | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| svc-001 | 算法服务-01 | algo-service-1 | 172.21.198.81 | 8746 | 10.179.182.121 | 9262 | active | 1 | 2026-05-31 21:29:06.139786+00:00 | 2026-05-31 21:29:06.139792+00:00 | NULL | NULL | NULL |
| svc-002 | 算法服务-02 | algo-service-2 | 10.37.59.34 | 8171 | 192.168.52.194 | 9356 | active | 2 | 2026-05-31 21:29:06.139795+00:00 | 2026-05-31 21:29:06.139797+00:00 | NULL | NULL | NULL |
| svc-003 | 算法服务-03 | algo-service-3 | 10.210.102.247 | 8315 | 172.18.233.208 | 9653 | inactive | 3 | 2026-05-31 21:29:06.139799+00:00 | 2026-05-31 21:29:06.139801+00:00 | NULL | NULL | NULL |
| svc-004 | 算法服务-04 | algo-service-4 | 172.27.154.79 | 8265 | 192.168.24.90 | 9711 | active | 4 | 2026-05-31 21:29:06.139804+00:00 | 2026-05-31 21:29:06.139806+00:00 | NULL | NULL | NULL |
| svc-005 | 算法服务-05 | algo-service-5 | 192.168.159.228 | 8500 | 10.128.186.191 | 9940 | active | 5 | 2026-05-31 21:29:06.139808+00:00 | 2026-05-31 21:29:06.139811+00:00 | NULL | NULL | NULL |
| svc-006 | 算法服务-06 | algo-service-6 | 172.26.224.119 | 8071 | 172.24.4.23 | 9356 | active | 6 | 2026-05-31 21:29:06.139813+00:00 | 2026-05-31 21:29:06.139815+00:00 | NULL | NULL | NULL |
| svc-007 | 算法服务-07 | algo-service-7 | 10.245.23.63 | 8845 | 10.122.61.137 | 9381 | active | 7 | 2026-05-31 21:29:06.139817+00:00 | 2026-05-31 21:29:06.139820+00:00 | NULL | NULL | NULL |
| svc-008 | 算法服务-08 | algo-service-8 | 10.142.2.28 | 8357 | 172.19.52.201 | 9306 | active | 8 | 2026-05-31 21:29:06.139822+00:00 | 2026-05-31 21:29:06.139824+00:00 | NULL | NULL | NULL |
| svc-009 | 算法服务-09 | algo-service-9 | 192.168.197.203 | 8745 | 10.42.147.27 | 9912 | active | 9 | 2026-05-31 21:29:06.139826+00:00 | 2026-05-31 21:29:06.139828+00:00 | NULL | NULL | NULL |
| svc-010 | 算法服务-10 | algo-service-10 | 10.19.206.178 | 8140 | 10.235.229.95 | 9799 | active | 10 | 2026-05-31 21:29:06.139831+00:00 | 2026-05-31 21:29:06.139833+00:00 | NULL | NULL | NULL |
| svc-011 | 算法服务-11 | algo-service-11 | 192.168.77.206 | 8092 | 10.226.243.178 | 9913 | inactive | 11 | 2026-05-31 21:29:06.139835+00:00 | 2026-05-31 21:29:06.139837+00:00 | NULL | NULL | NULL |
| svc-012 | 算法服务-12 | algo-service-12 | 10.241.68.113 | 8990 | 192.168.186.238 | 9698 | active | 12 | 2026-05-31 21:29:06.139839+00:00 | 2026-05-31 21:29:06.139842+00:00 | NULL | NULL | NULL |

---

## annotation

**主键**: `id`

**外键**:
- `deployment_id` -> `deployment.id`
- `device_id` -> `device.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| deployment_id | bigint | YES |  |
| device_id | bigint | YES |  |
| name | character varying | YES |  |
| type | character varying | NO |  |
| polygon_json | jsonb | NO |  |
| color | character varying | YES |  |
| id | bigint | NO | nextval('annotation_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (0 条)

*(空表)*

---

## clean_record

**主键**: `id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| type | character varying | YES |  |
| cutoff_time | timestamp with time zone | YES |  |
| status | character varying | NO |  |
| progress | numeric | NO |  |
| clean_size_bytes | bigint | NO |  |
| id | bigint | NO | nextval('clean_record_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (20 条)

| type | cutoff_time | status | progress | clean_size_bytes | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| video | 2024-04-17 13:38:39+00:00 | running | 4.90 | 85152877669 | 1 | 2026-05-31 21:29:06.680451+00:00 | 2026-05-31 21:29:06.680455+00:00 | NULL | NULL | NULL |
| log | 2023-12-15 18:17:42+00:00 | completed | 35.56 | 95042782721 | 2 | 2026-05-31 21:29:06.680456+00:00 | 2026-05-31 21:29:06.680458+00:00 | NULL | NULL | NULL |
| image | 2023-11-21 02:36:58+00:00 | failed | 4.14 | 104212858186 | 3 | 2026-05-31 21:29:06.680459+00:00 | 2026-05-31 21:29:06.680461+00:00 | NULL | NULL | NULL |
| image | 2023-05-12 16:49:43+00:00 | running | 8.76 | 27822562164 | 4 | 2026-05-31 21:29:06.680462+00:00 | 2026-05-31 21:29:06.680463+00:00 | NULL | NULL | NULL |
| video | 2023-03-31 20:14:27+00:00 | running | 87.90 | 22837061928 | 5 | 2026-05-31 21:29:06.680465+00:00 | 2026-05-31 21:29:06.680466+00:00 | NULL | NULL | NULL |
| image | 2023-01-25 10:59:18+00:00 | pending | 2.36 | 18704071276 | 6 | 2026-05-31 21:29:06.680467+00:00 | 2026-05-31 21:29:06.680469+00:00 | NULL | NULL | NULL |
| video | 2024-01-19 13:53:26+00:00 | completed | 11.10 | 24618358786 | 7 | 2026-05-31 21:29:06.680470+00:00 | 2026-05-31 21:29:06.680471+00:00 | NULL | NULL | NULL |
| image | 2023-11-11 12:24:25+00:00 | completed | 89.25 | 11960122784 | 8 | 2026-05-31 21:29:06.680473+00:00 | 2026-05-31 21:29:06.680474+00:00 | NULL | NULL | NULL |
| video | 2022-12-31 18:36:37+00:00 | pending | 32.56 | 76272630020 | 9 | 2026-05-31 21:29:06.680476+00:00 | 2026-05-31 21:29:06.680477+00:00 | NULL | NULL | NULL |
| image | 2023-10-11 23:39:52+00:00 | pending | 70.01 | 88286007719 | 10 | 2026-05-31 21:29:06.680478+00:00 | 2026-05-31 21:29:06.680480+00:00 | NULL | NULL | NULL |
| image | 2023-05-12 06:09:57+00:00 | pending | 40.59 | 106635472056 | 11 | 2026-05-31 21:29:06.680481+00:00 | 2026-05-31 21:29:06.680482+00:00 | NULL | NULL | NULL |
| log | 2023-01-21 21:20:58+00:00 | failed | 35.89 | 61927893459 | 12 | 2026-05-31 21:29:06.680484+00:00 | 2026-05-31 21:29:06.680485+00:00 | NULL | NULL | NULL |
| image | 2023-04-03 10:23:47+00:00 | completed | 49.97 | 25502223533 | 13 | 2026-05-31 21:29:06.680486+00:00 | 2026-05-31 21:29:06.680488+00:00 | NULL | NULL | NULL |
| video | 2023-05-01 12:26:06+00:00 | running | 17.37 | 54230626171 | 14 | 2026-05-31 21:29:06.680489+00:00 | 2026-05-31 21:29:06.680490+00:00 | NULL | NULL | NULL |
| log | 2023-10-27 14:28:33+00:00 | failed | 13.73 | 101713282035 | 15 | 2026-05-31 21:29:06.680492+00:00 | 2026-05-31 21:29:06.680493+00:00 | NULL | NULL | NULL |
| log | 2024-02-15 18:52:25+00:00 | completed | 94.48 | 62854344216 | 16 | 2026-05-31 21:29:06.680495+00:00 | 2026-05-31 21:29:06.680496+00:00 | NULL | NULL | NULL |
| log | 2023-12-13 19:43:45+00:00 | failed | 55.86 | 11147726907 | 17 | 2026-05-31 21:29:06.680497+00:00 | 2026-05-31 21:29:06.680499+00:00 | NULL | NULL | NULL |
| log | 2023-03-04 18:17:40+00:00 | running | 53.50 | 37310729374 | 18 | 2026-05-31 21:29:06.680500+00:00 | 2026-05-31 21:29:06.680502+00:00 | NULL | NULL | NULL |
| video | 2023-05-08 15:30:10+00:00 | pending | 47.52 | 7205727294 | 19 | 2026-05-31 21:29:06.680504+00:00 | 2026-05-31 21:29:06.680505+00:00 | NULL | NULL | NULL |
| video | 2024-02-24 19:06:00+00:00 | completed | 92.37 | 44573072923 | 20 | 2026-05-31 21:29:06.680506+00:00 | 2026-05-31 21:29:06.680508+00:00 | NULL | NULL | NULL |

---

## data_source

**主键**: `id`

**外键**:
- `region_id` -> `region.id`
- `device_id` -> `device.id`
- `org_id` -> `organization.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| name | character varying | NO |  |
| status | character varying | NO |  |
| rtsp_url | character varying | YES |  |
| push_url | character varying | YES |  |
| access_type | character varying | YES |  |
| longitude | character varying | YES |  |
| latitude | character varying | YES |  |
| data_source_type | character varying | YES |  |
| region | character varying | YES |  |
| org | character varying | YES |  |
| device | character varying | YES |  |
| remark | character varying | YES |  |
| memory_usage | integer | YES |  |
| disk_size | character varying | YES |  |
| disk_usage | integer | YES |  |
| id | bigint | NO | nextval('data_source_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |
| device_id | integer | YES |  |
| region_id | integer | YES |  |
| org_id | integer | YES |  |

### 数据 (0 条)

*(空表)*

---

## deployment

**主键**: `id`

**外键**:
- `algorithm_id` -> `algorithm.id`
- `service_id` -> `algorithm_service.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| name | character varying | NO |  |
| algorithm_id | bigint | YES |  |
| service_id | bigint | YES |  |
| status | character varying | NO |  |
| algorithm_status | character varying | NO |  |
| deployed_at | timestamp with time zone | YES |  |
| id | bigint | NO | nextval('deployment_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (20 条)

| name | algorithm_id | service_id | status | algorithm_status | deployed_at | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 布控任务-01 | 1 | 10 | active | stopped | 2025-07-05 11:24:05+00:00 | 1 | 2026-05-31 21:29:06.258128+00:00 | 2026-05-31 21:29:06.258133+00:00 | NULL | NULL | NULL |
| 布控任务-02 | 1 | 12 | active | running | 2024-03-28 10:00:14+00:00 | 2 | 2026-05-31 21:29:06.258136+00:00 | 2026-05-31 21:29:06.258138+00:00 | NULL | NULL | NULL |
| 布控任务-03 | 1 | 6 | stopped | running | 2024-05-11 08:47:43+00:00 | 3 | 2026-05-31 21:29:06.258140+00:00 | 2026-05-31 21:29:06.258142+00:00 | NULL | NULL | NULL |
| 布控任务-04 | 1 | 3 | paused | error | 2024-03-04 19:14:05+00:00 | 4 | 2026-05-31 21:29:06.258144+00:00 | 2026-05-31 21:29:06.258146+00:00 | NULL | NULL | NULL |
| 布控任务-05 | 1 | 2 | active | stopped | 2025-05-17 14:44:52+00:00 | 5 | 2026-05-31 21:29:06.258148+00:00 | 2026-05-31 21:29:06.258150+00:00 | NULL | NULL | NULL |
| 布控任务-06 | 1 | 8 | active | running | 2026-03-08 02:34:50+00:00 | 6 | 2026-05-31 21:29:06.258152+00:00 | 2026-05-31 21:29:06.258154+00:00 | NULL | NULL | NULL |
| 布控任务-07 | 1 | 1 | active | running | 2024-10-28 09:11:58+00:00 | 7 | 2026-05-31 21:29:06.258156+00:00 | 2026-05-31 21:29:06.258158+00:00 | NULL | NULL | NULL |
| 布控任务-08 | 1 | 10 | active | error | 2024-10-13 10:38:16+00:00 | 8 | 2026-05-31 21:29:06.258160+00:00 | 2026-05-31 21:29:06.258162+00:00 | NULL | NULL | NULL |
| 布控任务-09 | 1 | 11 | active | running | 2025-08-25 02:52:09+00:00 | 9 | 2026-05-31 21:29:06.258165+00:00 | 2026-05-31 21:29:06.258166+00:00 | NULL | NULL | NULL |
| 布控任务-10 | 1 | 7 | active | running | 2025-02-25 01:59:21+00:00 | 10 | 2026-05-31 21:29:06.258169+00:00 | 2026-05-31 21:29:06.258171+00:00 | NULL | NULL | NULL |
| 布控任务-11 | 1 | 11 | stopped | stopped | 2025-08-10 15:35:57+00:00 | 11 | 2026-05-31 21:29:06.258173+00:00 | 2026-05-31 21:29:06.258175+00:00 | NULL | NULL | NULL |
| 布控任务-12 | 1 | 7 | paused | running | 2024-01-25 05:58:35+00:00 | 12 | 2026-05-31 21:29:06.258177+00:00 | 2026-05-31 21:29:06.258179+00:00 | NULL | NULL | NULL |
| 布控任务-13 | 1 | 12 | active | error | 2025-10-28 03:23:02+00:00 | 13 | 2026-05-31 21:29:06.258181+00:00 | 2026-05-31 21:29:06.258183+00:00 | NULL | NULL | NULL |
| 布控任务-14 | 1 | 9 | active | running | 2026-01-31 17:24:55+00:00 | 14 | 2026-05-31 21:29:06.258185+00:00 | 2026-05-31 21:29:06.258187+00:00 | NULL | NULL | NULL |
| 布控任务-15 | 1 | 3 | paused | stopped | 2024-06-06 17:46:42+00:00 | 15 | 2026-05-31 21:29:06.258189+00:00 | 2026-05-31 21:29:06.258191+00:00 | NULL | NULL | NULL |
| 布控任务-16 | 1 | 9 | stopped | stopped | 2025-05-08 07:14:57+00:00 | 16 | 2026-05-31 21:29:06.258193+00:00 | 2026-05-31 21:29:06.258195+00:00 | NULL | NULL | NULL |
| 布控任务-17 | 1 | 7 | paused | running | 2025-08-06 18:54:00+00:00 | 17 | 2026-05-31 21:29:06.258198+00:00 | 2026-05-31 21:29:06.258200+00:00 | NULL | NULL | NULL |
| 布控任务-18 | 1 | 2 | active | stopped | 2025-11-06 15:35:28+00:00 | 18 | 2026-05-31 21:29:06.258202+00:00 | 2026-05-31 21:29:06.258204+00:00 | NULL | NULL | NULL |
| 布控任务-19 | 1 | 12 | active | error | 2024-08-20 11:57:40+00:00 | 19 | 2026-05-31 21:29:06.258206+00:00 | 2026-05-31 21:29:06.258208+00:00 | NULL | NULL | NULL |
| 布控任务-20 | 1 | 6 | paused | running | 2024-04-24 20:50:17+00:00 | 20 | 2026-05-31 21:29:06.258210+00:00 | 2026-05-31 21:29:06.258212+00:00 | NULL | NULL | NULL |

---

## deployment_device

**主键**: `id`

**外键**:
- `device_id` -> `device.id`
- `deployment_id` -> `deployment.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| deployment_id | bigint | NO |  |
| device_id | bigint | NO |  |
| id | bigint | NO | nextval('deployment_device_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (0 条)

*(空表)*

---

## deployment_schedule

**主键**: `id`

**外键**:
- `deployment_id` -> `deployment.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| deployment_id | bigint | NO |  |
| day_of_week | integer | NO |  |
| start_time | time without time zone | NO |  |
| end_time | time without time zone | NO |  |
| id | bigint | NO | nextval('deployment_schedule_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (106 条)

| deployment_id | day_of_week | start_time | end_time | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | 02:06:00 | 18:29:00 | 1 | 2026-05-31 21:29:06.287830+00:00 | 2026-05-31 21:29:06.287836+00:00 | NULL | NULL | NULL |
| 1 | 2 | 01:45:00 | 20:25:00 | 2 | 2026-05-31 21:29:06.287839+00:00 | 2026-05-31 21:29:06.287841+00:00 | NULL | NULL | NULL |
| 1 | 4 | 08:30:00 | 22:20:00 | 3 | 2026-05-31 21:29:06.287843+00:00 | 2026-05-31 21:29:06.287845+00:00 | NULL | NULL | NULL |
| 1 | 5 | 00:13:00 | 22:07:00 | 4 | 2026-05-31 21:29:06.287847+00:00 | 2026-05-31 21:29:06.287849+00:00 | NULL | NULL | NULL |
| 1 | 6 | 06:57:00 | 22:48:00 | 5 | 2026-05-31 21:29:06.287851+00:00 | 2026-05-31 21:29:06.287853+00:00 | NULL | NULL | NULL |
| 2 | 0 | 01:14:00 | 16:05:00 | 6 | 2026-05-31 21:29:06.287855+00:00 | 2026-05-31 21:29:06.287857+00:00 | NULL | NULL | NULL |
| 2 | 1 | 06:01:00 | 23:10:00 | 7 | 2026-05-31 21:29:06.287859+00:00 | 2026-05-31 21:29:06.287861+00:00 | NULL | NULL | NULL |
| 2 | 2 | 08:09:00 | 17:15:00 | 8 | 2026-05-31 21:29:06.287863+00:00 | 2026-05-31 21:29:06.287865+00:00 | NULL | NULL | NULL |
| 2 | 3 | 04:29:00 | 20:59:00 | 9 | 2026-05-31 21:29:06.287868+00:00 | 2026-05-31 21:29:06.287870+00:00 | NULL | NULL | NULL |
| 2 | 4 | 08:19:00 | 16:46:00 | 10 | 2026-05-31 21:29:06.287872+00:00 | 2026-05-31 21:29:06.287874+00:00 | NULL | NULL | NULL |
| 2 | 5 | 00:30:00 | 20:30:00 | 11 | 2026-05-31 21:29:06.287876+00:00 | 2026-05-31 21:29:06.287878+00:00 | NULL | NULL | NULL |
| 2 | 6 | 02:54:00 | 20:19:00 | 12 | 2026-05-31 21:29:06.287880+00:00 | 2026-05-31 21:29:06.287882+00:00 | NULL | NULL | NULL |
| 3 | 1 | 06:54:00 | 19:15:00 | 13 | 2026-05-31 21:29:06.287884+00:00 | 2026-05-31 21:29:06.287886+00:00 | NULL | NULL | NULL |
| 3 | 2 | 00:31:00 | 18:44:00 | 14 | 2026-05-31 21:29:06.287888+00:00 | 2026-05-31 21:29:06.287890+00:00 | NULL | NULL | NULL |
| 3 | 3 | 00:33:00 | 18:53:00 | 15 | 2026-05-31 21:29:06.287892+00:00 | 2026-05-31 21:29:06.287894+00:00 | NULL | NULL | NULL |
| 3 | 4 | 00:04:00 | 17:05:00 | 16 | 2026-05-31 21:29:06.287896+00:00 | 2026-05-31 21:29:06.287898+00:00 | NULL | NULL | NULL |
| 3 | 5 | 06:26:00 | 23:52:00 | 17 | 2026-05-31 21:29:06.287900+00:00 | 2026-05-31 21:29:06.287902+00:00 | NULL | NULL | NULL |
| 3 | 6 | 08:39:00 | 20:55:00 | 18 | 2026-05-31 21:29:06.287904+00:00 | 2026-05-31 21:29:06.287906+00:00 | NULL | NULL | NULL |
| 4 | 2 | 01:45:00 | 23:06:00 | 19 | 2026-05-31 21:29:06.287908+00:00 | 2026-05-31 21:29:06.287910+00:00 | NULL | NULL | NULL |
| 4 | 3 | 00:00:00 | 16:49:00 | 20 | 2026-05-31 21:29:06.287912+00:00 | 2026-05-31 21:29:06.287914+00:00 | NULL | NULL | NULL |
| 4 | 4 | 03:11:00 | 21:31:00 | 21 | 2026-05-31 21:29:06.287916+00:00 | 2026-05-31 21:29:06.287918+00:00 | NULL | NULL | NULL |
| 4 | 6 | 05:34:00 | 19:40:00 | 22 | 2026-05-31 21:29:06.287920+00:00 | 2026-05-31 21:29:06.287922+00:00 | NULL | NULL | NULL |
| 5 | 0 | 01:00:00 | 21:05:00 | 23 | 2026-05-31 21:29:06.287924+00:00 | 2026-05-31 21:29:06.287926+00:00 | NULL | NULL | NULL |
| 5 | 1 | 00:00:00 | 20:40:00 | 24 | 2026-05-31 21:29:06.287928+00:00 | 2026-05-31 21:29:06.287930+00:00 | NULL | NULL | NULL |
| 5 | 2 | 08:06:00 | 18:19:00 | 25 | 2026-05-31 21:29:06.287932+00:00 | 2026-05-31 21:29:06.287934+00:00 | NULL | NULL | NULL |
| 5 | 4 | 07:33:00 | 19:19:00 | 26 | 2026-05-31 21:29:06.287936+00:00 | 2026-05-31 21:29:06.287938+00:00 | NULL | NULL | NULL |
| 5 | 5 | 00:40:00 | 19:44:00 | 27 | 2026-05-31 21:29:06.287940+00:00 | 2026-05-31 21:29:06.287942+00:00 | NULL | NULL | NULL |
| 6 | 0 | 05:59:00 | 21:47:00 | 28 | 2026-05-31 21:29:06.287944+00:00 | 2026-05-31 21:29:06.287946+00:00 | NULL | NULL | NULL |
| 6 | 1 | 05:58:00 | 16:35:00 | 29 | 2026-05-31 21:29:06.287948+00:00 | 2026-05-31 21:29:06.287950+00:00 | NULL | NULL | NULL |
| 6 | 2 | 00:19:00 | 20:27:00 | 30 | 2026-05-31 21:29:06.287952+00:00 | 2026-05-31 21:29:06.287954+00:00 | NULL | NULL | NULL |
| 6 | 3 | 01:03:00 | 20:13:00 | 31 | 2026-05-31 21:29:06.287956+00:00 | 2026-05-31 21:29:06.287958+00:00 | NULL | NULL | NULL |
| 6 | 4 | 08:59:00 | 22:11:00 | 32 | 2026-05-31 21:29:06.287960+00:00 | 2026-05-31 21:29:06.287962+00:00 | NULL | NULL | NULL |
| 6 | 5 | 02:14:00 | 21:35:00 | 33 | 2026-05-31 21:29:06.287964+00:00 | 2026-05-31 21:29:06.287966+00:00 | NULL | NULL | NULL |
| 6 | 6 | 08:37:00 | 22:01:00 | 34 | 2026-05-31 21:29:06.287968+00:00 | 2026-05-31 21:29:06.287970+00:00 | NULL | NULL | NULL |
| 7 | 1 | 01:46:00 | 19:40:00 | 35 | 2026-05-31 21:29:06.287972+00:00 | 2026-05-31 21:29:06.287974+00:00 | NULL | NULL | NULL |
| 7 | 3 | 02:16:00 | 16:23:00 | 36 | 2026-05-31 21:29:06.287976+00:00 | 2026-05-31 21:29:06.287978+00:00 | NULL | NULL | NULL |
| 7 | 4 | 04:43:00 | 17:00:00 | 37 | 2026-05-31 21:29:06.287980+00:00 | 2026-05-31 21:29:06.287982+00:00 | NULL | NULL | NULL |
| 7 | 5 | 05:22:00 | 22:18:00 | 38 | 2026-05-31 21:29:06.287985+00:00 | 2026-05-31 21:29:06.287987+00:00 | NULL | NULL | NULL |
| 8 | 0 | 00:11:00 | 17:44:00 | 39 | 2026-05-31 21:29:06.287989+00:00 | 2026-05-31 21:29:06.287991+00:00 | NULL | NULL | NULL |
| 8 | 1 | 01:12:00 | 22:08:00 | 40 | 2026-05-31 21:29:06.287993+00:00 | 2026-05-31 21:29:06.287995+00:00 | NULL | NULL | NULL |
| 8 | 2 | 02:55:00 | 17:59:00 | 41 | 2026-05-31 21:29:06.287997+00:00 | 2026-05-31 21:29:06.287999+00:00 | NULL | NULL | NULL |
| 8 | 4 | 03:02:00 | 20:39:00 | 42 | 2026-05-31 21:29:06.288001+00:00 | 2026-05-31 21:29:06.288003+00:00 | NULL | NULL | NULL |
| 8 | 5 | 05:42:00 | 23:24:00 | 43 | 2026-05-31 21:29:06.288005+00:00 | 2026-05-31 21:29:06.288008+00:00 | NULL | NULL | NULL |
| 8 | 6 | 08:49:00 | 17:03:00 | 44 | 2026-05-31 21:29:06.288010+00:00 | 2026-05-31 21:29:06.288012+00:00 | NULL | NULL | NULL |
| 9 | 1 | 03:56:00 | 23:32:00 | 45 | 2026-05-31 21:29:06.288015+00:00 | 2026-05-31 21:29:06.288017+00:00 | NULL | NULL | NULL |
| 9 | 2 | 05:48:00 | 20:42:00 | 46 | 2026-05-31 21:29:06.288019+00:00 | 2026-05-31 21:29:06.288021+00:00 | NULL | NULL | NULL |
| 9 | 4 | 03:29:00 | 22:38:00 | 47 | 2026-05-31 21:29:06.288023+00:00 | 2026-05-31 21:29:06.288025+00:00 | NULL | NULL | NULL |
| 9 | 5 | 07:05:00 | 22:09:00 | 48 | 2026-05-31 21:29:06.288027+00:00 | 2026-05-31 21:29:06.288029+00:00 | NULL | NULL | NULL |
| 9 | 6 | 03:45:00 | 21:47:00 | 49 | 2026-05-31 21:29:06.288031+00:00 | 2026-05-31 21:29:06.288033+00:00 | NULL | NULL | NULL |
| 10 | 0 | 07:24:00 | 20:37:00 | 50 | 2026-05-31 21:29:06.288035+00:00 | 2026-05-31 21:29:06.288037+00:00 | NULL | NULL | NULL |
| 10 | 1 | 00:50:00 | 22:06:00 | 51 | 2026-05-31 21:29:06.288039+00:00 | 2026-05-31 21:29:06.288041+00:00 | NULL | NULL | NULL |
| 10 | 2 | 04:21:00 | 20:24:00 | 52 | 2026-05-31 21:29:06.288043+00:00 | 2026-05-31 21:29:06.288045+00:00 | NULL | NULL | NULL |
| 10 | 3 | 01:32:00 | 22:21:00 | 53 | 2026-05-31 21:29:06.288047+00:00 | 2026-05-31 21:29:06.288049+00:00 | NULL | NULL | NULL |
| 10 | 5 | 07:38:00 | 16:40:00 | 54 | 2026-05-31 21:29:06.288051+00:00 | 2026-05-31 21:29:06.288053+00:00 | NULL | NULL | NULL |
| 10 | 6 | 04:18:00 | 16:14:00 | 55 | 2026-05-31 21:29:06.288056+00:00 | 2026-05-31 21:29:06.288058+00:00 | NULL | NULL | NULL |
| 11 | 1 | 08:32:00 | 21:05:00 | 56 | 2026-05-31 21:29:06.288060+00:00 | 2026-05-31 21:29:06.288062+00:00 | NULL | NULL | NULL |
| 11 | 2 | 04:11:00 | 20:41:00 | 57 | 2026-05-31 21:29:06.288064+00:00 | 2026-05-31 21:29:06.288066+00:00 | NULL | NULL | NULL |
| 11 | 3 | 08:13:00 | 17:30:00 | 58 | 2026-05-31 21:29:06.288068+00:00 | 2026-05-31 21:29:06.288070+00:00 | NULL | NULL | NULL |
| 11 | 4 | 00:37:00 | 22:13:00 | 59 | 2026-05-31 21:29:06.288072+00:00 | 2026-05-31 21:29:06.288074+00:00 | NULL | NULL | NULL |
| 11 | 5 | 08:50:00 | 19:15:00 | 60 | 2026-05-31 21:29:06.288076+00:00 | 2026-05-31 21:29:06.288078+00:00 | NULL | NULL | NULL |
| 11 | 6 | 07:09:00 | 23:10:00 | 61 | 2026-05-31 21:29:06.288080+00:00 | 2026-05-31 21:29:06.288082+00:00 | NULL | NULL | NULL |
| 12 | 0 | 00:46:00 | 19:04:00 | 62 | 2026-05-31 21:29:06.288084+00:00 | 2026-05-31 21:29:06.288086+00:00 | NULL | NULL | NULL |
| 12 | 1 | 08:34:00 | 22:16:00 | 63 | 2026-05-31 21:29:06.288088+00:00 | 2026-05-31 21:29:06.288090+00:00 | NULL | NULL | NULL |
| 12 | 2 | 02:07:00 | 20:58:00 | 64 | 2026-05-31 21:29:06.288092+00:00 | 2026-05-31 21:29:06.288094+00:00 | NULL | NULL | NULL |
| 12 | 3 | 04:38:00 | 23:15:00 | 65 | 2026-05-31 21:29:06.288096+00:00 | 2026-05-31 21:29:06.288098+00:00 | NULL | NULL | NULL |
| 12 | 4 | 02:02:00 | 21:54:00 | 66 | 2026-05-31 21:29:06.288101+00:00 | 2026-05-31 21:29:06.288103+00:00 | NULL | NULL | NULL |
| 12 | 6 | 04:26:00 | 23:22:00 | 67 | 2026-05-31 21:29:06.288105+00:00 | 2026-05-31 21:29:06.288107+00:00 | NULL | NULL | NULL |
| 13 | 1 | 02:35:00 | 22:26:00 | 68 | 2026-05-31 21:29:06.288109+00:00 | 2026-05-31 21:29:06.288111+00:00 | NULL | NULL | NULL |
| 13 | 2 | 02:35:00 | 22:58:00 | 69 | 2026-05-31 21:29:06.288113+00:00 | 2026-05-31 21:29:06.288115+00:00 | NULL | NULL | NULL |
| 13 | 3 | 02:08:00 | 20:19:00 | 70 | 2026-05-31 21:29:06.288117+00:00 | 2026-05-31 21:29:06.288119+00:00 | NULL | NULL | NULL |
| 13 | 4 | 07:30:00 | 17:15:00 | 71 | 2026-05-31 21:29:06.288121+00:00 | 2026-05-31 21:29:06.288123+00:00 | NULL | NULL | NULL |
| 13 | 6 | 08:26:00 | 21:16:00 | 72 | 2026-05-31 21:29:06.288125+00:00 | 2026-05-31 21:29:06.288127+00:00 | NULL | NULL | NULL |
| 14 | 0 | 01:57:00 | 20:47:00 | 73 | 2026-05-31 21:29:06.288129+00:00 | 2026-05-31 21:29:06.288131+00:00 | NULL | NULL | NULL |
| 14 | 1 | 00:20:00 | 16:15:00 | 74 | 2026-05-31 21:29:06.288133+00:00 | 2026-05-31 21:29:06.288135+00:00 | NULL | NULL | NULL |
| 14 | 2 | 04:37:00 | 20:57:00 | 75 | 2026-05-31 21:29:06.288137+00:00 | 2026-05-31 21:29:06.288139+00:00 | NULL | NULL | NULL |
| 14 | 3 | 08:13:00 | 23:39:00 | 76 | 2026-05-31 21:29:06.288141+00:00 | 2026-05-31 21:29:06.288143+00:00 | NULL | NULL | NULL |
| 14 | 5 | 00:31:00 | 17:06:00 | 77 | 2026-05-31 21:29:06.288145+00:00 | 2026-05-31 21:29:06.288147+00:00 | NULL | NULL | NULL |
| 14 | 6 | 02:44:00 | 18:29:00 | 78 | 2026-05-31 21:29:06.288149+00:00 | 2026-05-31 21:29:06.288151+00:00 | NULL | NULL | NULL |
| 15 | 2 | 01:25:00 | 22:33:00 | 79 | 2026-05-31 21:29:06.288153+00:00 | 2026-05-31 21:29:06.288155+00:00 | NULL | NULL | NULL |
| 15 | 3 | 07:52:00 | 21:24:00 | 80 | 2026-05-31 21:29:06.288157+00:00 | 2026-05-31 21:29:06.288159+00:00 | NULL | NULL | NULL |
| 15 | 4 | 01:55:00 | 18:42:00 | 81 | 2026-05-31 21:29:06.288161+00:00 | 2026-05-31 21:29:06.288163+00:00 | NULL | NULL | NULL |
| 15 | 5 | 07:48:00 | 18:09:00 | 82 | 2026-05-31 21:29:06.288165+00:00 | 2026-05-31 21:29:06.288167+00:00 | NULL | NULL | NULL |
| 16 | 1 | 06:33:00 | 18:36:00 | 83 | 2026-05-31 21:29:06.288169+00:00 | 2026-05-31 21:29:06.288171+00:00 | NULL | NULL | NULL |
| 16 | 4 | 01:29:00 | 23:08:00 | 84 | 2026-05-31 21:29:06.288173+00:00 | 2026-05-31 21:29:06.288175+00:00 | NULL | NULL | NULL |
| 16 | 5 | 07:40:00 | 20:24:00 | 85 | 2026-05-31 21:29:06.288177+00:00 | 2026-05-31 21:29:06.288179+00:00 | NULL | NULL | NULL |
| 16 | 6 | 01:42:00 | 21:49:00 | 86 | 2026-05-31 21:29:06.288182+00:00 | 2026-05-31 21:29:06.288183+00:00 | NULL | NULL | NULL |
| 17 | 1 | 07:46:00 | 18:10:00 | 87 | 2026-05-31 21:29:06.288186+00:00 | 2026-05-31 21:29:06.288187+00:00 | NULL | NULL | NULL |
| 17 | 3 | 04:39:00 | 23:45:00 | 88 | 2026-05-31 21:29:06.288190+00:00 | 2026-05-31 21:29:06.288192+00:00 | NULL | NULL | NULL |
| 17 | 4 | 02:32:00 | 17:16:00 | 89 | 2026-05-31 21:29:06.288194+00:00 | 2026-05-31 21:29:06.288196+00:00 | NULL | NULL | NULL |
| 17 | 6 | 01:16:00 | 16:38:00 | 90 | 2026-05-31 21:29:06.288198+00:00 | 2026-05-31 21:29:06.288200+00:00 | NULL | NULL | NULL |
| 18 | 0 | 02:40:00 | 16:36:00 | 91 | 2026-05-31 21:29:06.288202+00:00 | 2026-05-31 21:29:06.288204+00:00 | NULL | NULL | NULL |
| 18 | 1 | 06:14:00 | 21:11:00 | 92 | 2026-05-31 21:29:06.288206+00:00 | 2026-05-31 21:29:06.288208+00:00 | NULL | NULL | NULL |
| 18 | 3 | 05:58:00 | 16:51:00 | 93 | 2026-05-31 21:29:06.288210+00:00 | 2026-05-31 21:29:06.288212+00:00 | NULL | NULL | NULL |
| 18 | 4 | 04:01:00 | 23:15:00 | 94 | 2026-05-31 21:29:06.288214+00:00 | 2026-05-31 21:29:06.288216+00:00 | NULL | NULL | NULL |
| 18 | 6 | 02:50:00 | 22:14:00 | 95 | 2026-05-31 21:29:06.288218+00:00 | 2026-05-31 21:29:06.288220+00:00 | NULL | NULL | NULL |
| 19 | 0 | 04:52:00 | 18:51:00 | 96 | 2026-05-31 21:29:06.288222+00:00 | 2026-05-31 21:29:06.288224+00:00 | NULL | NULL | NULL |
| 19 | 1 | 06:59:00 | 20:14:00 | 97 | 2026-05-31 21:29:06.288226+00:00 | 2026-05-31 21:29:06.288228+00:00 | NULL | NULL | NULL |
| 19 | 3 | 00:07:00 | 19:18:00 | 98 | 2026-05-31 21:29:06.288230+00:00 | 2026-05-31 21:29:06.288232+00:00 | NULL | NULL | NULL |
| 19 | 4 | 01:47:00 | 18:43:00 | 99 | 2026-05-31 21:29:06.288234+00:00 | 2026-05-31 21:29:06.288236+00:00 | NULL | NULL | NULL |
| 19 | 5 | 04:51:00 | 18:42:00 | 100 | 2026-05-31 21:29:06.288238+00:00 | 2026-05-31 21:29:06.288240+00:00 | NULL | NULL | NULL |

*（仅显示前100条，共 106 条）*

---

## device

**主键**: `id`

**外键**:
- `org_id` -> `organization.id`
- `region_id` -> `region.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| device_code | character varying | NO |  |
| name | character varying | NO |  |
| status | character varying | NO |  |
| access_type | character varying | NO |  |
| device_type | character varying | YES |  |
| longitude | numeric | YES |  |
| latitude | numeric | YES |  |
| region_id | bigint | YES |  |
| org_id | bigint | YES |  |
| memory_usage | numeric | YES |  |
| disk_size | bigint | YES |  |
| disk_usage | numeric | YES |  |
| remark | character varying | YES |  |
| id | bigint | NO | nextval('device_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (4 条)

| device_code | name | status | access_type | device_type | longitude | latitude | region_id | org_id | memory_usage | disk_size | disk_usage | remark | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-1780299107097 | 设备1 | active | direct | NULL | NULL | NULL | 17 | 8 | NULL | NULL | NULL |  | 51 | 2026-05-31 23:31:49.243486+00:00 | 2026-05-31 23:31:49.243490+00:00 | NULL | NULL | NULL |
| DEV-1780300732883 | 设备2 | active | direct | NULL | NULL | NULL | 17 | 8 | NULL | NULL | NULL |  | 52 | 2026-05-31 23:58:55.043684+00:00 | 2026-05-31 23:58:55.043689+00:00 | NULL | NULL | NULL |
| DEV-1780300750083 | 设备3 | active | direct | NULL | NULL | NULL | 17 | 8 | NULL | NULL | NULL |  | 53 | 2026-05-31 23:59:12.255318+00:00 | 2026-05-31 23:59:12.255328+00:00 | NULL | NULL | NULL |
| DEV-1780300881483 | 设备1 | active | direct | NULL | NULL | NULL | 19 | 8 | NULL | NULL | NULL |  | 54 | 2026-06-01 00:01:23.693833+00:00 | 2026-06-01 00:01:23.693842+00:00 | NULL | NULL | NULL |

---

## device_stream

**主键**: `id`

**外键**:
- `device_id` -> `device.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| device_id | bigint | NO |  |
| stream_type | character varying | NO |  |
| stream_url | character varying | YES |  |
| push_url | character varying | YES |  |
| resolution | character varying | YES |  |
| fps | integer | YES |  |
| codec | character varying | YES |  |
| is_primary | boolean | NO |  |
| status | character varying | NO |  |
| id | bigint | NO | nextval('device_stream_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (0 条)

*(空表)*

---

## dispose_tag

**主键**: `id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| tag_name | character varying | NO |  |
| tag_color | character varying | YES |  |
| usage_count | integer | NO |  |
| remark | character varying | YES |  |
| id | bigint | NO | nextval('dispose_tag_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (6 条)

| tag_name | tag_color | usage_count | remark | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 已处理 | #67C23A | 0 | NULL | 7 | 2026-05-31 21:29:06.436991+00:00 | 2026-05-31 21:29:06.436996+00:00 | NULL | NULL | NULL |
| 待核实 | #E6A23C | 0 | NULL | 8 | 2026-05-31 21:29:06.436999+00:00 | 2026-05-31 21:29:06.437001+00:00 | NULL | NULL | NULL |
| 误报 | #909399 | 0 | NULL | 9 | 2026-05-31 21:29:06.437003+00:00 | 2026-05-31 21:29:06.437005+00:00 | NULL | NULL | NULL |
| 紧急 | #F56C6C | 0 | NULL | 10 | 2026-05-31 21:29:06.437008+00:00 | 2026-05-31 21:29:06.437010+00:00 | NULL | NULL | NULL |
| 需跟进 | #409EFF | 0 | NULL | 11 | 2026-05-31 21:29:06.437012+00:00 | 2026-05-31 21:29:06.437014+00:00 | NULL | NULL | NULL |
| 已归档 | #909399 | 0 | NULL | 12 | 2026-05-31 21:29:06.437016+00:00 | 2026-05-31 21:29:06.437018+00:00 | NULL | NULL | NULL |

---

## event_type

**主键**: `id`

**外键**:
- `algorithm_id` -> `algorithm.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| algorithm_id | bigint | YES |  |
| name | character varying | NO |  |
| description | character varying | YES |  |
| category | character varying | NO |  |
| severity | integer | NO |  |
| id | bigint | NO | nextval('event_type_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (16 条)

| algorithm_id | name | description | category | severity | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 疑似事故 | 检测到疑似交通事故 | detection | 5 | 1 | 2026-05-31 21:29:06.119609+00:00 | 2026-05-31 21:29:06.119614+00:00 | NULL | NULL | NULL |
| 1 | 作业人员 | 检测到道路作业人员 | alarm | 3 | 2 | 2026-05-31 21:29:06.119618+00:00 | 2026-05-31 21:29:06.119620+00:00 | NULL | NULL | NULL |
| 1 | 交通阻塞 | 检测到交通阻塞 | analysis | 3 | 3 | 2026-05-31 21:29:06.119622+00:00 | 2026-05-31 21:29:06.119624+00:00 | NULL | NULL | NULL |
| 1 | 异常停车 | 检测到异常停车行为 | alarm | 4 | 4 | 2026-05-31 21:29:06.119627+00:00 | 2026-05-31 21:29:06.119629+00:00 | NULL | NULL | NULL |
| 1 | 烟雾 | 检测到烟雾 | analysis | 2 | 5 | 2026-05-31 21:29:06.119631+00:00 | 2026-05-31 21:29:06.119633+00:00 | NULL | NULL | NULL |
| 1 | 作业车辆识别 | 识别到作业车辆 | analysis | 3 | 6 | 2026-05-31 21:29:06.119636+00:00 | 2026-05-31 21:29:06.119638+00:00 | NULL | NULL | NULL |
| 1 | 非机动车驶入 | 检测到非机动车驶入 | analysis | 2 | 7 | 2026-05-31 21:29:06.119640+00:00 | 2026-05-31 21:29:06.119642+00:00 | NULL | NULL | NULL |
| 1 | 占用应急车道 | 检测到占用应急车道 | alarm | 5 | 8 | 2026-05-31 21:29:06.119645+00:00 | 2026-05-31 21:29:06.119647+00:00 | NULL | NULL | NULL |
| 1 | 逆向行驶 | 检测到逆向行驶 | alarm | 3 | 9 | 2026-05-31 21:29:06.119649+00:00 | 2026-05-31 21:29:06.119651+00:00 | NULL | NULL | NULL |
| 1 | 通过卡车数量 | 统计通过卡车数量 | detection | 3 | 10 | 2026-05-31 21:29:06.119653+00:00 | 2026-05-31 21:29:06.119656+00:00 | NULL | NULL | NULL |
| 1 | 通过大客车数量 | 统计通过大客车数量 | detection | 2 | 11 | 2026-05-31 21:29:06.119658+00:00 | 2026-05-31 21:29:06.119660+00:00 | NULL | NULL | NULL |
| 1 | 通过摩托车数量 | 统计通过摩托车数量 | analysis | 5 | 12 | 2026-05-31 21:29:06.119662+00:00 | 2026-05-31 21:29:06.119664+00:00 | NULL | NULL | NULL |
| 1 | 通过小汽车数量 | 统计通过小汽车数量 | alarm | 2 | 13 | 2026-05-31 21:29:06.119667+00:00 | 2026-05-31 21:29:06.119669+00:00 | NULL | NULL | NULL |
| 1 | 下行车流量 | 统计下行车流量 | analysis | 3 | 14 | 2026-05-31 21:29:06.119671+00:00 | 2026-05-31 21:29:06.119673+00:00 | NULL | NULL | NULL |
| 1 | 上行车流量 | 统计上行车流量 | alarm | 5 | 15 | 2026-05-31 21:29:06.119675+00:00 | 2026-05-31 21:29:06.119678+00:00 | NULL | NULL | NULL |
| 1 | 行人闯入 | 检测到行人闯入 | detection | 4 | 16 | 2026-05-31 21:29:06.119680+00:00 | 2026-05-31 21:29:06.119682+00:00 | NULL | NULL | NULL |

---

## event_type_pt_weight

**主键**: `id`

**外键**:
- `pt_weight_file_id` -> `pt_weight_file.id`
- `event_type_id` -> `event_type.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| id | bigint | NO | nextval('event_type_pt_weight_id_seq'::regclass) |
| event_type_id | bigint | NO |  |
| pt_weight_file_id | bigint | NO |  |
| created_at | timestamp with time zone | NO | now() |
| updated_at | timestamp with time zone | NO | now() |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (0 条)

*(空表)*

---

## file

**主键**: `id`

**外键**:
- `warning_event_id` -> `warning_event.id`
- `device_id` -> `device.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| file_name | character varying | NO |  |
| file_size_bytes | bigint | YES |  |
| duration_seconds | integer | YES |  |
| device_id | bigint | YES |  |
| file_type | character varying | YES |  |
| storage_path | character varying | YES |  |
| url | character varying | YES |  |
| id | bigint | NO | nextval('file_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |
| warning_event_id | integer | YES |  |

### 数据 (0 条)

*(空表)*

---

## firmware

**主键**: `id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| name | character varying | YES |  |
| version | character varying | NO |  |
| applicable_version | character varying | YES |  |
| force_upgrade | boolean | NO |  |
| description | text | YES |  |
| id | bigint | NO | nextval('firmware_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (15 条)

| name | version | applicable_version | force_upgrade | description | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 固件升级包-01 | v5.8.36 | v3.x | False | At expect finally town. | 1 | 2026-05-31 21:29:06.602529+00:00 | 2026-05-31 21:29:06.602535+00:00 | NULL | NULL | NULL |
| 固件升级包-02 | v1.3.62 | v3.x | False | Authority produce per career public street us. | 2 | 2026-05-31 21:29:06.602539+00:00 | 2026-05-31 21:29:06.602541+00:00 | NULL | NULL | NULL |
| 固件升级包-03 | v1.8.92 | v1.x | False | Structure million affect business true. | 3 | 2026-05-31 21:29:06.602543+00:00 | 2026-05-31 21:29:06.602546+00:00 | NULL | NULL | NULL |
| 固件升级包-04 | v1.8.0 | v3.x | False | 等级发布决定在线产品进入. | 4 | 2026-05-31 21:29:06.602548+00:00 | 2026-05-31 21:29:06.602550+00:00 | NULL | NULL | NULL |
| 固件升级包-05 | v2.9.9 | v4.x | True | Well debate industry. | 5 | 2026-05-31 21:29:06.602553+00:00 | 2026-05-31 21:29:06.602555+00:00 | NULL | NULL | NULL |
| 固件升级包-06 | v4.9.52 | v1.x | False | 那么法律基本任何信息现在. | 6 | 2026-05-31 21:29:06.602557+00:00 | 2026-05-31 21:29:06.602560+00:00 | NULL | NULL | NULL |
| 固件升级包-07 | v1.4.58 | v1.x | False | Decade world thank. | 7 | 2026-05-31 21:29:06.602562+00:00 | 2026-05-31 21:29:06.602564+00:00 | NULL | NULL | NULL |
| 固件升级包-08 | v3.5.71 | v2.x | False | Skin choice nice reduce relationship. | 8 | 2026-05-31 21:29:06.602567+00:00 | 2026-05-31 21:29:06.602569+00:00 | NULL | NULL | NULL |
| 固件升级包-09 | v1.9.75 | v2.x | False | 能力科技国家中国什么无法这个. | 9 | 2026-05-31 21:29:06.602571+00:00 | 2026-05-31 21:29:06.602574+00:00 | NULL | NULL | NULL |
| 固件升级包-10 | v2.7.22 | v2.x | False | 精华孩子专业的人报告更多作者. | 10 | 2026-05-31 21:29:06.602576+00:00 | 2026-05-31 21:29:06.602578+00:00 | NULL | NULL | NULL |
| 固件升级包-11 | v1.4.33 | v1.x | True | 得到推荐根据显示. | 11 | 2026-05-31 21:29:06.602581+00:00 | 2026-05-31 21:29:06.602583+00:00 | NULL | NULL | NULL |
| 固件升级包-12 | v3.1.13 | v3.x | True | 一起同时地区. | 12 | 2026-05-31 21:29:06.602586+00:00 | 2026-05-31 21:29:06.602588+00:00 | NULL | NULL | NULL |
| 固件升级包-13 | v4.0.19 | v4.x | False | Bit idea difference establish approach social. | 13 | 2026-05-31 21:29:06.602590+00:00 | 2026-05-31 21:29:06.602593+00:00 | NULL | NULL | NULL |
| 固件升级包-14 | v4.0.77 | v4.x | False | 一点根据工作结果设备. | 14 | 2026-05-31 21:29:06.602595+00:00 | 2026-05-31 21:29:06.602597+00:00 | NULL | NULL | NULL |
| 固件升级包-15 | v5.1.97 | v4.x | False | Language brother protect offer necessary. | 15 | 2026-05-31 21:29:06.602600+00:00 | 2026-05-31 21:29:06.602602+00:00 | NULL | NULL | NULL |

---

## gb28181_device

**主键**: `id`

**外键**:
- `device_id` -> `device.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| device_id | bigint | NO |  |
| manufacturer | character varying | YES |  |
| model | character varying | YES |  |
| sip_server_id | character varying | YES |  |
| sip_device_id | character varying | YES |  |
| status | character varying | NO |  |
| channels_json | jsonb | NO |  |
| id | bigint | NO | nextval('gb28181_device_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (0 条)

*(空表)*

---

## license

**主键**: `id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| license_key | character varying | NO |  |
| type | character varying | YES |  |
| device_limit | integer | NO |  |
| used_count | integer | NO |  |
| expire_date | date | YES |  |
| status | character varying | NO |  |
| id | bigint | NO | nextval('license_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (2 条)

| license_key | type | device_limit | used_count | expire_date | status | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2dd8d29a-e6c0-4214-89c2-1c252994fe82 | enterprise | 500 | 255 | 2026-12-31 | active | 1 | 2026-05-31 21:29:06.591053+00:00 | 2026-05-31 21:29:06.591058+00:00 | NULL | NULL | NULL |
| 4e926fc0-bfc0-4bdc-a9a4-0af6c6bb524a | trial | 50 | 34 | 2025-06-30 | active | 2 | 2026-05-31 21:29:06.591061+00:00 | 2026-05-31 21:29:06.591063+00:00 | NULL | NULL | NULL |

---

## linkage_rule

**主键**: `id`

**外键**:
- `algorithm_id` -> `algorithm.id`
- `event_type_id` -> `event_type.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| rule_name | character varying | NO |  |
| trigger_mode | character varying | NO |  |
| algorithm_id | bigint | YES |  |
| event_type_id | bigint | YES |  |
| level | integer | NO |  |
| delay_push | integer | NO |  |
| is_compliant | character varying | YES |  |
| unit | character varying | YES |  |
| action_type | character varying | YES |  |
| status | character varying | NO |  |
| link | character varying | YES |  |
| content | text | YES |  |
| importance_level | integer | NO |  |
| send_frequency | character varying | YES |  |
| push_channels | jsonb | YES |  |
| app_id | character varying | YES |  |
| app_secret | character varying | YES |  |
| template_id | character varying | YES |  |
| push_target | character varying | YES |  |
| remark | character varying | YES |  |
| id | bigint | NO | nextval('linkage_rule_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (25 条)

| rule_name | trigger_mode | algorithm_id | event_type_id | level | delay_push | is_compliant | unit | action_type | status | link | content | importance_level | send_frequency | push_channels | app_id | app_secret | template_id | push_target | remark | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 联动规则-01 | MANUAL | 1 | 10 | 1 | 30 | non_compliant | Odonnell, Knight and Bruce | webhook | inactive | http://white-martin.com/ | 设计特别一样作者环境简介这种. | 5 | immediate | {'app': True, 'sms': False, 'email': True} | 3617b9d0-94a9-46f3-aa7e-84b0d697c93f | NULL | d2651295-8fe2-4cf0-a3d9-9ae4a6fed5d9 | 15983468299 | Nor customer side girl machine. | 1 | 2026-05-31 21:29:06.345454+00:00 | 2026-05-31 21:29:06.345459+00:00 | NULL | NULL | NULL |
| 联动规则-02 | MANUAL | 1 | 4 | 4 | 5 | NULL | Williams-Stewart | push | inactive | NULL | 帮助程序联系以上今天那个更新. | 3 | 1hour | {'app': True, 'sms': False, 'email': True} | NULL | NULL | NULL | NULL | Water artist poor such. | 2 | 2026-05-31 21:29:06.345461+00:00 | 2026-05-31 21:29:06.345463+00:00 | NULL | NULL | NULL |
| 联动规则-03 | MANUAL | 1 | 6 | 2 | 5 | non_compliant | Powell-Thomas | email | active | https://ck.cn/ | Better quickly stock today hundred. | 2 | 15min | {'app': True, 'sms': False, 'email': False} | NULL | $9A3_CnYPu | NULL | NULL | NULL | 3 | 2026-05-31 21:29:06.345465+00:00 | 2026-05-31 21:29:06.345467+00:00 | NULL | NULL | NULL |
| 联动规则-04 | MANUAL | 1 | 3 | 2 | 5 | compliant | 思优科技有限公司 | snapshot | active | http://www.rodriguez.com/ | Everyone easy entire detail test manage popular. | 1 | 5min | {'app': True, 'sms': True, 'email': False} | b8cab934-f37c-4442-9c0a-ea831a78ec37 | V1S%a$Ok%B | NULL | NULL | NULL | 4 | 2026-05-31 21:29:06.345469+00:00 | 2026-05-31 21:29:06.345471+00:00 | NULL | NULL | NULL |
| 联动规则-05 | MANUAL | 1 | 10 | 5 | 10 | compliant | Williams-Morales | push | active | NULL | Art husband family should. | 4 | immediate | {'app': True, 'sms': False, 'email': True} | NULL | NULL | NULL | NULL | 都是人民发展欢迎. | 5 | 2026-05-31 21:29:06.345473+00:00 | 2026-05-31 21:29:06.345475+00:00 | NULL | NULL | NULL |
| 联动规则-06 | MANUAL | 1 | 6 | 1 | 10 | NULL | 思优传媒有限公司 | push | active | NULL | Another involve appear population. | 1 | 15min | {'app': True, 'sms': False, 'email': True} | NULL | NULL | NULL | NULL | NULL | 6 | 2026-05-31 21:29:06.345477+00:00 | 2026-05-31 21:29:06.345479+00:00 | NULL | NULL | NULL |
| 联动规则-07 | MANUAL | 1 | 4 | 4 | 10 | compliant | 昊嘉传媒有限公司 | sms | inactive | NULL | 不是发表显示所以朋友这里. | 3 | immediate | {'app': True, 'sms': False, 'email': True} | NULL | NULL | NULL | NULL | NULL | 7 | 2026-05-31 21:29:06.345481+00:00 | 2026-05-31 21:29:06.345483+00:00 | NULL | NULL | NULL |
| 联动规则-08 | MANUAL | 1 | 12 | 5 | 5 | compliant | 新宇龙信息信息有限公司 | sms | active | NULL | Nature since walk message. | 1 | 15min | {'app': True, 'sms': False, 'email': False} | 61e3dcc3-1c49-4fea-9f1b-ecabd5993abb | NULL | ab352f90-ba5b-4ce6-a6da-c209d3e2b223 | NULL | NULL | 8 | 2026-05-31 21:29:06.345485+00:00 | 2026-05-31 21:29:06.345487+00:00 | NULL | NULL | NULL |
| 联动规则-09 | MANUAL | 1 | 12 | 4 | 10 | compliant | Jenkins, Glenn and Torres | email | inactive | http://www.18.cn/ | Cause offer during bag eight agree worker. | 5 | 15min | {'app': True, 'sms': True, 'email': True} | NULL | NULL | NULL | NULL | NULL | 9 | 2026-05-31 21:29:06.345489+00:00 | 2026-05-31 21:29:06.345491+00:00 | NULL | NULL | NULL |
| 联动规则-10 | AUTO | 1 | 6 | 1 | 5 | non_compliant | Bonilla-Johnson | webhook | active | NULL | Body single offer top charge. | 2 | immediate | {'app': True, 'sms': False, 'email': True} | NULL | %&f9XXDxTb | NULL | NULL | 的话要求不断实现. | 10 | 2026-05-31 21:29:06.345493+00:00 | 2026-05-31 21:29:06.345495+00:00 | NULL | NULL | NULL |
| 联动规则-11 | AUTO | 1 | 15 | 1 | 0 | compliant | Gaines Inc | email | active | NULL | 公司其他回复文化. | 1 | immediate | {'app': True, 'sms': True, 'email': False} | NULL | #SA1Ob2c^K | NULL | NULL | Serve major positive leave wife card. | 11 | 2026-05-31 21:29:06.345497+00:00 | 2026-05-31 21:29:06.345499+00:00 | NULL | NULL | NULL |
| 联动规则-12 | AUTO | 1 | 7 | 3 | 0 | NULL | 良诺传媒有限公司 | push | active | NULL | 不断政府参加那么男人系列同时. | 5 | 5min | {'app': True, 'sms': True, 'email': True} | NULL | &0%TVcD$KT | 387a0fb6-846d-4e9a-8b9b-f0f63b861a77 | (263)783-1265 | 学生报告回复国内图片提供. | 12 | 2026-05-31 21:29:06.345501+00:00 | 2026-05-31 21:29:06.345503+00:00 | NULL | NULL | NULL |
| 联动规则-13 | AUTO | 1 | 1 | 5 | 5 | compliant | Davis, Wilson and Armstrong | sms | active | NULL | 公司方法介绍孩子有关论坛不断. | 5 | 1hour | {'app': True, 'sms': False, 'email': True} | 89eb5d76-8191-4556-bc99-08c5e4fb48eb | NULL | NULL | NULL | NULL | 13 | 2026-05-31 21:29:06.345505+00:00 | 2026-05-31 21:29:06.345507+00:00 | NULL | NULL | NULL |
| 联动规则-14 | MANUAL | 1 | 14 | 3 | 30 | non_compliant | 超艺科技有限公司 | push | inactive | NULL | 以及设备完成以及成为. | 3 | 1hour | {'app': True, 'sms': False, 'email': True} | NULL | NULL | NULL | 696-948-2652x59807 | 现在设备原因目前更多国际. | 14 | 2026-05-31 21:29:06.345509+00:00 | 2026-05-31 21:29:06.345511+00:00 | NULL | NULL | NULL |
| 联动规则-15 | AUTO | 1 | 1 | 1 | 5 | compliant | 巨奥科技有限公司 | email | active | http://www.stevens.com/ | 查看得到其他简介起来. | 5 | 5min | {'app': True, 'sms': False, 'email': True} | NULL | NULL | aa8732a6-6af0-4773-b063-9212647322b2 | 18870701896 | NULL | 15 | 2026-05-31 21:29:06.345513+00:00 | 2026-05-31 21:29:06.345514+00:00 | NULL | NULL | NULL |
| 联动规则-16 | MANUAL | 1 | 12 | 3 | 0 | non_compliant | Scott LLC | webhook | active | https://www.taylor-welch.com/ | 因此会员更多能够联系拥有. | 2 | 5min | {'app': True, 'sms': False, 'email': True} | NULL | NULL | NULL | NULL | 虽然联系生活我们怎么一个详细注意. | 16 | 2026-05-31 21:29:06.345516+00:00 | 2026-05-31 21:29:06.345518+00:00 | NULL | NULL | NULL |
| 联动规则-17 | AUTO | 1 | 15 | 3 | 0 | NULL | Wong, Johnson and Williams | snapshot | inactive | NULL | 登录很多最新学生系列发生. | 5 | 5min | {'app': True, 'sms': True, 'email': False} | 4d397849-ed1c-48e0-a03f-432369b0fe96 | NULL | NULL | 13392683054 | My per relate throughout sometimes future. | 17 | 2026-05-31 21:29:06.345520+00:00 | 2026-05-31 21:29:06.345522+00:00 | NULL | NULL | NULL |
| 联动规则-18 | AUTO | 1 | 6 | 5 | 0 | non_compliant | Wood, Harper and Watkins | snapshot | active | NULL | 全部提供成功也是地址对于文化. | 3 | 15min | {'app': True, 'sms': True, 'email': False} | NULL | NULL | NULL | NULL | NULL | 18 | 2026-05-31 21:29:06.345524+00:00 | 2026-05-31 21:29:06.345526+00:00 | NULL | NULL | NULL |
| 联动规则-19 | AUTO | 1 | 6 | 2 | 0 | non_compliant | Maynard and Sons | email | active | NULL | 公司都是所以开始. | 1 | immediate | {'app': True, 'sms': False, 'email': False} | 007a6e34-bba9-48f9-9f7b-e17c9cff1288 | @oCcY0wVi8 | 378b7440-c8a2-4d24-9b50-65566d8c4638 | NULL | NULL | 19 | 2026-05-31 21:29:06.345528+00:00 | 2026-05-31 21:29:06.345530+00:00 | NULL | NULL | NULL |
| 联动规则-20 | MANUAL | 1 | 4 | 1 | 0 | compliant | 国讯传媒有限公司 | push | active | https://www.weihou.cn/ | 客户什么具有. | 3 | 15min | {'app': True, 'sms': True, 'email': False} | NULL | _Y8Q+fnR1M | ac9fa416-3484-4e6a-8eab-3b767000fc9d | NULL | 要求最大点击为了觉得为了. | 20 | 2026-05-31 21:29:06.345532+00:00 | 2026-05-31 21:29:06.345534+00:00 | NULL | NULL | NULL |
| 联动规则-21 | AUTO | 1 | 16 | 3 | 10 | non_compliant | Tyler-Harris | email | inactive | NULL | Indicate produce anyone when future whatever ba... | 1 | 1hour | {'app': True, 'sms': False, 'email': True} | NULL | %KOm@oxj9G | NULL | NULL | NULL | 21 | 2026-05-31 21:29:06.345536+00:00 | 2026-05-31 21:29:06.345538+00:00 | NULL | NULL | NULL |
| 联动规则-22 | MANUAL | 1 | 7 | 5 | 5 | compliant | 方正科技科技有限公司 | webhook | inactive | NULL | List around best light drive design. | 2 | immediate | {'app': True, 'sms': False, 'email': False} | NULL | NULL | NULL | NULL | NULL | 22 | 2026-05-31 21:29:06.345540+00:00 | 2026-05-31 21:29:06.345542+00:00 | NULL | NULL | NULL |
| 联动规则-23 | MANUAL | 1 | 4 | 5 | 30 | compliant | Crosby-Jones | sms | active | NULL | Discussion receive their yet south discuss itself. | 2 | immediate | {'app': True, 'sms': True, 'email': False} | NULL | NULL | 882adde1-d4cb-413a-a3e5-6cd3de71a4e1 | 13793775577 | 之后所以安全经验. | 23 | 2026-05-31 21:29:06.345544+00:00 | 2026-05-31 21:29:06.345546+00:00 | NULL | NULL | NULL |
| 联动规则-24 | MANUAL | 1 | 12 | 2 | 30 | non_compliant | 商软冠联网络有限公司 | snapshot | active | http://www.zeng.cn/ | 一直什么显示发现一般. | 2 | 1hour | {'app': True, 'sms': False, 'email': True} | f63e55b5-8a71-4073-9ff8-20ba9608f0bd | %KrKmgXy3* | NULL | NULL | NULL | 24 | 2026-05-31 21:29:06.345548+00:00 | 2026-05-31 21:29:06.345550+00:00 | NULL | NULL | NULL |
| 联动规则-25 | AUTO | 1 | 9 | 2 | 0 | compliant | Prince Inc | email | inactive | NULL | Between between keep reach put. | 2 | 1hour | {'app': True, 'sms': False, 'email': True} | NULL | NULL | NULL | 001-759-831-3010x7399 | 同时上海成为各种经济活动一切. | 25 | 2026-05-31 21:29:06.345552+00:00 | 2026-05-31 21:29:06.345554+00:00 | NULL | NULL | NULL |

---

## linkage_rule_device

**主键**: `id`

**外键**:
- `device_id` -> `device.id`
- `linkage_rule_id` -> `linkage_rule.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| linkage_rule_id | bigint | NO |  |
| device_id | bigint | NO |  |
| id | bigint | NO | nextval('linkage_rule_device_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (0 条)

*(空表)*

---

## menu

**主键**: `id`

**外键**:
- `parent_id` -> `menu.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| name | character varying | NO |  |
| path | character varying | YES |  |
| hidden | boolean | NO |  |
| parent_id | bigint | YES |  |
| sort | integer | NO |  |
| component | character varying | YES |  |
| title | character varying | YES |  |
| icon | character varying | YES |  |
| id | bigint | NO | nextval('menu_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (19 条)

| name | path | hidden | parent_id | sort | component | title | icon | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 首页 | /dashboard | False | NULL | 1 | Dashboard | 首页 | HomeFilled | 1 | 2026-05-31 21:29:05.955438+00:00 | 2026-05-31 21:29:05.955444+00:00 | NULL | NULL | NULL |
| 设备管理 | /device | False | NULL | 2 | Layout | 设备管理 | VideoCamera | 2 | 2026-05-31 21:29:05.955448+00:00 | 2026-05-31 21:29:05.955451+00:00 | NULL | NULL | NULL |
| 算法管理 | /algorithm | False | NULL | 3 | Layout | 算法管理 | Cpu | 6 | 2026-05-31 21:29:05.955470+00:00 | 2026-05-31 21:29:05.955473+00:00 | NULL | NULL | NULL |
| 布控管理 | /deployment | False | NULL | 4 | Deployment | 布控管理 | Aim | 9 | 2026-05-31 21:29:05.955487+00:00 | 2026-05-31 21:29:05.955490+00:00 | NULL | NULL | NULL |
| 联动规则 | /linkage | False | NULL | 5 | Layout | 联动规则 | Link | 10 | 2026-05-31 21:29:05.955493+00:00 | 2026-05-31 21:29:05.955496+00:00 | NULL | NULL | NULL |
| 系统设置 | /system | False | NULL | 6 | Layout | 系统设置 | Setting | 13 | 2026-05-31 21:29:05.955510+00:00 | 2026-05-31 21:29:05.955512+00:00 | NULL | NULL | NULL |
| 用户中心 | /user | False | NULL | 7 | Layout | 用户中心 | User | 16 | 2026-05-31 21:29:05.955527+00:00 | 2026-05-31 21:29:05.955529+00:00 | NULL | NULL | NULL |
| 设备列表 | /device/list | False | 2 | 1 | DeviceList | 设备列表 | List | 3 | 2026-05-31 21:29:05.955454+00:00 | 2026-05-31 21:29:05.965112+00:00 | NULL | NULL | NULL |
| 设备分组 | /device/group | False | 2 | 2 | DeviceGroup | 设备分组 | FolderOpened | 4 | 2026-05-31 21:29:05.955459+00:00 | 2026-05-31 21:29:05.965119+00:00 | NULL | NULL | NULL |
| 区域管理 | /device/region | False | 2 | 3 | Region | 区域管理 | MapLocation | 5 | 2026-05-31 21:29:05.955465+00:00 | 2026-05-31 21:29:05.965122+00:00 | NULL | NULL | NULL |
| 算法列表 | /algorithm/list | False | 6 | 1 | AlgorithmList | 算法列表 | Grid | 7 | 2026-05-31 21:29:05.955476+00:00 | 2026-05-31 21:29:05.965125+00:00 | NULL | NULL | NULL |
| 事件类型 | /algorithm/event | False | 6 | 2 | EventType | 事件类型 | Bell | 8 | 2026-05-31 21:29:05.955482+00:00 | 2026-05-31 21:29:05.965128+00:00 | NULL | NULL | NULL |
| 规则列表 | /linkage/rule | False | 10 | 1 | LinkageRule | 规则列表 | Document | 11 | 2026-05-31 21:29:05.955499+00:00 | 2026-05-31 21:29:05.965130+00:00 | NULL | NULL | NULL |
| 推送历史 | /linkage/history | False | 10 | 2 | PushHistory | 推送历史 | Timer | 12 | 2026-05-31 21:29:05.955504+00:00 | 2026-05-31 21:29:05.965133+00:00 | NULL | NULL | NULL |
| 视频设置 | /system/video | False | 13 | 1 | VideoSetting | 视频设置 | VideoPlay | 14 | 2026-05-31 21:29:05.955515+00:00 | 2026-05-31 21:29:05.965136+00:00 | NULL | NULL | NULL |
| 文件管理 | /system/file | False | 13 | 2 | FileManager | 文件管理 | Folder | 15 | 2026-05-31 21:29:05.955521+00:00 | 2026-05-31 21:29:05.965139+00:00 | NULL | NULL | NULL |
| 用户管理 | /user/list | False | 16 | 1 | UserList | 用户管理 | UserFilled | 17 | 2026-05-31 21:29:05.955532+00:00 | 2026-05-31 21:29:05.965141+00:00 | NULL | NULL | NULL |
| 角色管理 | /user/role | False | 16 | 2 | RoleManage | 角色管理 | Medal | 18 | 2026-05-31 21:29:05.955538+00:00 | 2026-05-31 21:29:05.965144+00:00 | NULL | NULL | NULL |
| 组织管理 | /user/org | False | 16 | 3 | OrgManage | 组织管理 | OfficeBuilding | 19 | 2026-05-31 21:29:05.955543+00:00 | 2026-05-31 21:29:05.965147+00:00 | NULL | NULL | NULL |

---

## microservice

**主键**: `id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| code | character varying | YES |  |
| name | character varying | YES |  |
| service_name | character varying | YES |  |
| ip | character varying | YES |  |
| port | integer | YES |  |
| status | character varying | NO |  |
| cpu_usage | numeric | YES |  |
| memory_usage | numeric | YES |  |
| id | bigint | NO | nextval('microservice_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (4 条)

| code | name | service_name | ip | port | status | cpu_usage | memory_usage | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NULL | 设备服务 | device-service | 10.104.145.225 | 8081 | active | 57.27 | 72.83 | 1 | 2026-05-31 21:29:06.718769+00:00 | 2026-05-31 21:29:06.718773+00:00 | NULL | NULL | NULL |
| NULL | 算法服务 | algorithm-service | 172.28.148.232 | 8082 | active | 60.30 | 74.96 | 2 | 2026-05-31 21:29:06.718776+00:00 | 2026-05-31 21:29:06.718778+00:00 | NULL | NULL | NULL |
| NULL | 告警服务 | warning-service | 192.168.159.107 | 8083 | active | 20.91 | 30.15 | 3 | 2026-05-31 21:29:06.718780+00:00 | 2026-05-31 21:29:06.718782+00:00 | NULL | NULL | NULL |
| NULL | 存储服务 | storage-service | 10.213.193.255 | 8084 | active | 25.70 | 82.01 | 4 | 2026-05-31 21:29:06.718784+00:00 | 2026-05-31 21:29:06.718786+00:00 | NULL | NULL | NULL |

---

## onvif_device

**主键**: `id`

**外键**:
- `device_id` -> `device.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| device_id | bigint | NO |  |
| manufacturer | character varying | YES |  |
| model | character varying | YES |  |
| ip | character varying | YES |  |
| port | integer | YES |  |
| status | character varying | NO |  |
| profiles_json | jsonb | NO |  |
| id | bigint | NO | nextval('onvif_device_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (0 条)

*(空表)*

---

## operation_log

**主键**: `id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| username | character varying | YES |  |
| action | character varying | YES |  |
| ip | character varying | YES |  |
| result | character varying | YES |  |
| description | character varying | YES |  |
| action_time | timestamp with time zone | YES |  |
| id | bigint | NO | nextval('operation_log_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |
| method | character varying | YES |  |
| path | character varying | YES |  |
| status_code | integer | YES |  |

### 数据 (1237 条)

| username | action | ip | result | description | action_time | id | created_at | updated_at | created_by | updated_by | deleted_at | method | path | status_code |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| user027 | NULL | 142.65.246.17 | success | 删除设备 | 2025-12-08 04:22:04+00:00 | 1 | 2026-05-31 21:29:06.654529+00:00 | 2026-05-31 21:29:06.654533+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user008 | NULL | 37.103.63.236 | failure | 修改算法 | 2024-10-06 06:17:16+00:00 | 2 | 2026-05-31 21:29:06.654535+00:00 | 2026-05-31 21:29:06.654537+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user027 | NULL | 95.54.253.87 | success | 创建用户 | 2024-12-15 16:47:42+00:00 | 3 | 2026-05-31 21:29:06.654538+00:00 | 2026-05-31 21:29:06.654540+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user020 | NULL | 68.124.130.8 | success | 修改规则 | 2026-03-28 19:23:20+00:00 | 4 | 2026-05-31 21:29:06.654541+00:00 | 2026-05-31 21:29:06.654542+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user011 | NULL | 3.97.32.142 | failure | 查看设备 | 2024-12-02 18:13:51+00:00 | 5 | 2026-05-31 21:29:06.654544+00:00 | 2026-05-31 21:29:06.654545+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user030 | NULL | 1.35.10.213 | success | 创建用户 | 2025-04-26 17:17:35+00:00 | 6 | 2026-05-31 21:29:06.654547+00:00 | 2026-05-31 21:29:06.654548+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user017 | NULL | 64.147.19.150 | success | 创建算法 | 2026-05-13 01:31:16+00:00 | 7 | 2026-05-31 21:29:06.654549+00:00 | 2026-05-31 21:29:06.654551+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user007 | NULL | 195.146.123.187 | success | 创建用户 | 2026-02-26 14:00:47+00:00 | 8 | 2026-05-31 21:29:06.654552+00:00 | 2026-05-31 21:29:06.654553+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user012 | NULL | 192.32.32.211 | success | 创建设备 | 2025-07-09 14:21:21+00:00 | 9 | 2026-05-31 21:29:06.654555+00:00 | 2026-05-31 21:29:06.654556+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user014 | NULL | 90.176.252.0 | success | 分配角色 | 2024-11-25 03:34:02+00:00 | 10 | 2026-05-31 21:29:06.654558+00:00 | 2026-05-31 21:29:06.654559+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user026 | NULL | 42.94.158.94 | success | 分配角色 | 2025-03-19 08:06:21+00:00 | 11 | 2026-05-31 21:29:06.654561+00:00 | 2026-05-31 21:29:06.654562+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user004 | NULL | 111.232.216.221 | success | 修改配置 | 2024-11-13 18:27:45+00:00 | 12 | 2026-05-31 21:29:06.654563+00:00 | 2026-05-31 21:29:06.654565+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user022 | NULL | 22.249.193.19 | success | 修改规则 | 2025-06-24 05:26:51+00:00 | 13 | 2026-05-31 21:29:06.654566+00:00 | 2026-05-31 21:29:06.654568+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user025 | NULL | 157.45.147.209 | success | 登录 | 2025-11-25 09:57:21+00:00 | 14 | 2026-05-31 21:29:06.654569+00:00 | 2026-05-31 21:29:06.654570+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user020 | NULL | 187.45.176.120 | failure | 删除规则 | 2025-09-03 02:19:07+00:00 | 15 | 2026-05-31 21:29:06.654572+00:00 | 2026-05-31 21:29:06.654573+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user001 | NULL | 125.224.62.153 | failure | 修改设备 | 2025-02-17 07:35:27+00:00 | 16 | 2026-05-31 21:29:06.654575+00:00 | 2026-05-31 21:29:06.654576+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user019 | NULL | 164.221.52.149 | success | 创建算法 | 2024-08-03 14:55:16+00:00 | 17 | 2026-05-31 21:29:06.654578+00:00 | 2026-05-31 21:29:06.654579+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user014 | NULL | 83.9.130.0 | success | 登出 | 2024-07-23 18:01:58+00:00 | 18 | 2026-05-31 21:29:06.654580+00:00 | 2026-05-31 21:29:06.654582+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user018 | NULL | 173.210.109.229 | failure | 删除设备 | 2025-03-14 07:12:43+00:00 | 19 | 2026-05-31 21:29:06.654583+00:00 | 2026-05-31 21:29:06.654585+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user017 | NULL | 192.180.139.82 | success | 创建组织 | 2024-09-20 10:07:58+00:00 | 20 | 2026-05-31 21:29:06.654586+00:00 | 2026-05-31 21:29:06.654587+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user005 | NULL | 115.60.247.169 | success | 修改角色 | 2024-10-18 07:41:47+00:00 | 21 | 2026-05-31 21:29:06.654589+00:00 | 2026-05-31 21:29:06.654590+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user017 | NULL | 42.3.0.22 | failure | 修改设备 | 2024-08-08 21:16:54+00:00 | 22 | 2026-05-31 21:29:06.654592+00:00 | 2026-05-31 21:29:06.654593+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user004 | NULL | 60.206.103.208 | success | 删除用户 | 2026-03-07 01:59:31+00:00 | 23 | 2026-05-31 21:29:06.654595+00:00 | 2026-05-31 21:29:06.654596+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user018 | NULL | 215.29.253.149 | failure | 分配角色 | 2026-04-21 16:25:00+00:00 | 24 | 2026-05-31 21:29:06.654597+00:00 | 2026-05-31 21:29:06.654599+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user005 | NULL | 19.97.249.183 | success | 修改算法 | 2024-06-29 10:40:25+00:00 | 25 | 2026-05-31 21:29:06.654600+00:00 | 2026-05-31 21:29:06.654602+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user014 | NULL | 81.186.136.48 | failure | 登录 | 2025-07-03 19:12:17+00:00 | 26 | 2026-05-31 21:29:06.654603+00:00 | 2026-05-31 21:29:06.654604+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user018 | NULL | 211.168.47.202 | failure | 修改规则 | 2025-06-25 16:34:16+00:00 | 27 | 2026-05-31 21:29:06.654606+00:00 | 2026-05-31 21:29:06.654607+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user005 | NULL | 52.79.251.172 | failure | 修改算法 | 2025-07-29 04:08:58+00:00 | 28 | 2026-05-31 21:29:06.654609+00:00 | 2026-05-31 21:29:06.654610+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user010 | NULL | 18.79.10.13 | success | 查看日志 | 2025-02-10 13:37:18+00:00 | 29 | 2026-05-31 21:29:06.654611+00:00 | 2026-05-31 21:29:06.654613+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user009 | NULL | 131.131.195.15 | failure | 删除规则 | 2025-03-08 14:08:25+00:00 | 30 | 2026-05-31 21:29:06.654614+00:00 | 2026-05-31 21:29:06.654616+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user021 | NULL | 13.249.139.62 | success | 登出 | 2026-04-21 03:57:38+00:00 | 31 | 2026-05-31 21:29:06.654617+00:00 | 2026-05-31 21:29:06.654618+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user022 | NULL | 70.211.253.13 | success | 修改用户 | 2024-12-13 10:15:43+00:00 | 32 | 2026-05-31 21:29:06.654620+00:00 | 2026-05-31 21:29:06.654621+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user027 | NULL | 162.243.125.115 | success | 导出报表 | 2026-03-01 03:22:48+00:00 | 33 | 2026-05-31 21:29:06.654623+00:00 | 2026-05-31 21:29:06.654624+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user025 | NULL | 121.92.254.238 | success | 登录 | 2026-02-05 06:32:43+00:00 | 34 | 2026-05-31 21:29:06.654625+00:00 | 2026-05-31 21:29:06.654629+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user021 | NULL | 60.249.190.43 | failure | 删除用户 | 2024-06-09 06:05:33+00:00 | 35 | 2026-05-31 21:29:06.654631+00:00 | 2026-05-31 21:29:06.654632+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user025 | NULL | 158.29.104.21 | success | 删除算法 | 2024-11-15 03:17:47+00:00 | 36 | 2026-05-31 21:29:06.654634+00:00 | 2026-05-31 21:29:06.654635+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user008 | NULL | 186.57.144.190 | success | 分配角色 | 2025-09-21 21:08:27+00:00 | 37 | 2026-05-31 21:29:06.654636+00:00 | 2026-05-31 21:29:06.654638+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user024 | NULL | 70.244.229.48 | success | 登录 | 2025-09-09 20:42:37+00:00 | 38 | 2026-05-31 21:29:06.654639+00:00 | 2026-05-31 21:29:06.654641+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user030 | NULL | 108.196.135.236 | success | 分配角色 | 2025-02-13 14:54:14+00:00 | 39 | 2026-05-31 21:29:06.654642+00:00 | 2026-05-31 21:29:06.654643+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user001 | NULL | 40.26.81.125 | success | 修改规则 | 2024-08-20 05:22:49+00:00 | 40 | 2026-05-31 21:29:06.654645+00:00 | 2026-05-31 21:29:06.654646+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user015 | NULL | 3.96.10.164 | failure | 登录 | 2025-07-13 12:37:45+00:00 | 41 | 2026-05-31 21:29:06.654648+00:00 | 2026-05-31 21:29:06.654649+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user019 | NULL | 9.219.27.170 | success | 创建用户 | 2025-09-01 19:18:27+00:00 | 42 | 2026-05-31 21:29:06.654650+00:00 | 2026-05-31 21:29:06.654652+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user029 | NULL | 170.156.100.4 | success | 删除算法 | 2025-08-20 05:03:55+00:00 | 43 | 2026-05-31 21:29:06.654653+00:00 | 2026-05-31 21:29:06.654655+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user028 | NULL | 87.44.131.204 | success | 删除用户 | 2025-07-13 15:51:34+00:00 | 44 | 2026-05-31 21:29:06.654656+00:00 | 2026-05-31 21:29:06.654657+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user021 | NULL | 170.90.134.252 | success | 登录 | 2025-01-24 18:46:26+00:00 | 45 | 2026-05-31 21:29:06.654659+00:00 | 2026-05-31 21:29:06.654660+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user004 | NULL | 130.85.238.63 | success | 删除设备 | 2024-12-29 05:37:02+00:00 | 46 | 2026-05-31 21:29:06.654662+00:00 | 2026-05-31 21:29:06.654663+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user011 | NULL | 91.205.253.41 | success | 删除算法 | 2024-12-17 01:37:01+00:00 | 47 | 2026-05-31 21:29:06.654664+00:00 | 2026-05-31 21:29:06.654666+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user025 | NULL | 140.48.210.230 | success | 修改配置 | 2025-05-28 01:46:25+00:00 | 48 | 2026-05-31 21:29:06.654667+00:00 | 2026-05-31 21:29:06.654669+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user021 | NULL | 126.171.126.202 | success | 修改组织 | 2025-09-16 07:39:17+00:00 | 49 | 2026-05-31 21:29:06.654670+00:00 | 2026-05-31 21:29:06.654672+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user015 | NULL | 215.186.23.52 | failure | 删除规则 | 2025-10-26 07:23:24+00:00 | 50 | 2026-05-31 21:29:06.654673+00:00 | 2026-05-31 21:29:06.654674+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user002 | NULL | 193.34.12.104 | failure | 修改算法 | 2025-11-28 01:02:35+00:00 | 51 | 2026-05-31 21:29:06.654676+00:00 | 2026-05-31 21:29:06.654677+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user022 | NULL | 18.246.210.66 | success | 创建算法 | 2026-03-18 01:25:58+00:00 | 52 | 2026-05-31 21:29:06.654679+00:00 | 2026-05-31 21:29:06.654680+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user028 | NULL | 193.184.202.161 | failure | 登出 | 2025-08-30 13:31:32+00:00 | 53 | 2026-05-31 21:29:06.654681+00:00 | 2026-05-31 21:29:06.654683+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user012 | NULL | 44.240.81.96 | success | 创建规则 | 2025-07-04 07:17:11+00:00 | 54 | 2026-05-31 21:29:06.654684+00:00 | 2026-05-31 21:29:06.654686+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user009 | NULL | 203.56.197.95 | failure | 修改角色 | 2026-05-05 00:34:05+00:00 | 55 | 2026-05-31 21:29:06.654687+00:00 | 2026-05-31 21:29:06.654688+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user006 | NULL | 110.77.108.84 | success | 修改规则 | 2025-02-28 05:16:01+00:00 | 56 | 2026-05-31 21:29:06.654690+00:00 | 2026-05-31 21:29:06.654691+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user003 | NULL | 72.251.149.9 | success | 修改用户 | 2026-03-19 12:15:04+00:00 | 57 | 2026-05-31 21:29:06.654693+00:00 | 2026-05-31 21:29:06.654694+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user001 | NULL | 64.252.117.131 | failure | 分配角色 | 2025-02-19 14:21:33+00:00 | 58 | 2026-05-31 21:29:06.654696+00:00 | 2026-05-31 21:29:06.654697+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user021 | NULL | 197.60.249.164 | success | 查看日志 | 2024-08-04 15:19:16+00:00 | 59 | 2026-05-31 21:29:06.654698+00:00 | 2026-05-31 21:29:06.654700+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user007 | NULL | 220.53.233.194 | success | 修改配置 | 2024-10-22 14:04:41+00:00 | 60 | 2026-05-31 21:29:06.654701+00:00 | 2026-05-31 21:29:06.654703+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user024 | NULL | 106.156.239.78 | success | 删除规则 | 2025-03-17 02:08:51+00:00 | 61 | 2026-05-31 21:29:06.654704+00:00 | 2026-05-31 21:29:06.654705+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user006 | NULL | 176.128.151.132 | success | 修改组织 | 2025-08-17 08:16:19+00:00 | 62 | 2026-05-31 21:29:06.654707+00:00 | 2026-05-31 21:29:06.654708+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user012 | NULL | 151.51.137.66 | success | 创建用户 | 2025-04-09 18:05:44+00:00 | 63 | 2026-05-31 21:29:06.654710+00:00 | 2026-05-31 21:29:06.654711+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user005 | NULL | 16.199.191.214 | success | 删除设备 | 2024-09-15 14:04:43+00:00 | 64 | 2026-05-31 21:29:06.654713+00:00 | 2026-05-31 21:29:06.654714+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user013 | NULL | 109.252.123.34 | success | 创建设备 | 2025-12-08 20:31:46+00:00 | 65 | 2026-05-31 21:29:06.654716+00:00 | 2026-05-31 21:29:06.654717+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user025 | NULL | 117.253.87.159 | success | 删除设备 | 2024-07-26 21:34:50+00:00 | 66 | 2026-05-31 21:29:06.654718+00:00 | 2026-05-31 21:29:06.654720+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user022 | NULL | 7.244.61.238 | success | 修改组织 | 2025-04-03 07:15:05+00:00 | 67 | 2026-05-31 21:29:06.654721+00:00 | 2026-05-31 21:29:06.654723+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user022 | NULL | 204.92.70.134 | success | 修改组织 | 2025-02-04 23:29:09+00:00 | 68 | 2026-05-31 21:29:06.654724+00:00 | 2026-05-31 21:29:06.654725+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user017 | NULL | 157.70.238.246 | success | 查看设备 | 2025-10-10 00:26:49+00:00 | 69 | 2026-05-31 21:29:06.654727+00:00 | 2026-05-31 21:29:06.654728+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user030 | NULL | 18.79.42.246 | success | 删除用户 | 2025-02-20 16:50:12+00:00 | 70 | 2026-05-31 21:29:06.654730+00:00 | 2026-05-31 21:29:06.654731+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user004 | NULL | 156.25.223.41 | failure | 修改算法 | 2025-01-07 19:07:54+00:00 | 71 | 2026-05-31 21:29:06.654732+00:00 | 2026-05-31 21:29:06.654734+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user006 | NULL | 139.150.199.114 | success | 修改组织 | 2026-04-27 13:07:58+00:00 | 72 | 2026-05-31 21:29:06.654735+00:00 | 2026-05-31 21:29:06.654737+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user007 | NULL | 53.6.140.67 | success | 登出 | 2025-08-26 06:40:26+00:00 | 73 | 2026-05-31 21:29:06.654738+00:00 | 2026-05-31 21:29:06.654739+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user029 | NULL | 36.128.216.181 | failure | 创建设备 | 2025-10-02 07:32:33+00:00 | 74 | 2026-05-31 21:29:06.654741+00:00 | 2026-05-31 21:29:06.654742+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user021 | NULL | 4.29.46.33 | failure | 创建用户 | 2025-08-10 01:34:58+00:00 | 75 | 2026-05-31 21:29:06.654744+00:00 | 2026-05-31 21:29:06.654745+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user009 | NULL | 100.228.83.149 | success | 导出报表 | 2025-02-25 20:28:48+00:00 | 76 | 2026-05-31 21:29:06.654747+00:00 | 2026-05-31 21:29:06.654748+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user005 | NULL | 41.191.199.87 | success | 修改配置 | 2024-11-08 11:55:19+00:00 | 77 | 2026-05-31 21:29:06.654750+00:00 | 2026-05-31 21:29:06.654754+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user014 | NULL | 92.21.144.248 | success | 修改规则 | 2025-10-17 22:15:26+00:00 | 78 | 2026-05-31 21:29:06.654755+00:00 | 2026-05-31 21:29:06.654757+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user020 | NULL | 120.154.50.183 | success | 修改配置 | 2026-05-04 18:29:38+00:00 | 79 | 2026-05-31 21:29:06.654758+00:00 | 2026-05-31 21:29:06.654760+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user023 | NULL | 215.5.192.180 | success | 修改角色 | 2025-03-22 18:15:46+00:00 | 80 | 2026-05-31 21:29:06.654761+00:00 | 2026-05-31 21:29:06.654762+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user002 | NULL | 75.254.132.220 | failure | 创建规则 | 2025-08-25 07:57:49+00:00 | 81 | 2026-05-31 21:29:06.654764+00:00 | 2026-05-31 21:29:06.654765+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user029 | NULL | 132.115.203.247 | success | 创建用户 | 2024-09-09 05:02:22+00:00 | 82 | 2026-05-31 21:29:06.654767+00:00 | 2026-05-31 21:29:06.654768+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user024 | NULL | 169.169.197.20 | success | 创建用户 | 2025-08-16 06:07:21+00:00 | 83 | 2026-05-31 21:29:06.654769+00:00 | 2026-05-31 21:29:06.654771+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user014 | NULL | 107.171.143.86 | success | 修改规则 | 2026-05-14 04:31:08+00:00 | 84 | 2026-05-31 21:29:06.654772+00:00 | 2026-05-31 21:29:06.654773+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user004 | NULL | 47.195.118.69 | success | 登录 | 2024-10-03 05:02:55+00:00 | 85 | 2026-05-31 21:29:06.654775+00:00 | 2026-05-31 21:29:06.654776+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user026 | NULL | 59.191.25.182 | success | 修改算法 | 2025-01-25 14:23:57+00:00 | 86 | 2026-05-31 21:29:06.654778+00:00 | 2026-05-31 21:29:06.654779+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user007 | NULL | 172.178.72.124 | success | 删除用户 | 2025-11-30 18:54:54+00:00 | 87 | 2026-05-31 21:29:06.654780+00:00 | 2026-05-31 21:29:06.654782+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user003 | NULL | 165.104.205.19 | success | 修改用户 | 2025-09-02 07:18:38+00:00 | 88 | 2026-05-31 21:29:06.654783+00:00 | 2026-05-31 21:29:06.654784+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user009 | NULL | 52.137.220.25 | success | 创建组织 | 2025-01-07 19:58:30+00:00 | 89 | 2026-05-31 21:29:06.654786+00:00 | 2026-05-31 21:29:06.654787+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user011 | NULL | 129.91.127.174 | success | 删除算法 | 2024-10-22 20:24:33+00:00 | 90 | 2026-05-31 21:29:06.654789+00:00 | 2026-05-31 21:29:06.654790+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user011 | NULL | 11.200.66.154 | success | 修改组织 | 2026-01-06 01:47:09+00:00 | 91 | 2026-05-31 21:29:06.654791+00:00 | 2026-05-31 21:29:06.654793+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user030 | NULL | 6.250.187.22 | success | 创建组织 | 2025-05-29 20:56:39+00:00 | 92 | 2026-05-31 21:29:06.654794+00:00 | 2026-05-31 21:29:06.654795+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user019 | NULL | 35.115.184.139 | success | 删除规则 | 2024-12-13 16:51:10+00:00 | 93 | 2026-05-31 21:29:06.654797+00:00 | 2026-05-31 21:29:06.654798+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user002 | NULL | 16.140.39.64 | success | 删除规则 | 2025-11-22 19:26:09+00:00 | 94 | 2026-05-31 21:29:06.654800+00:00 | 2026-05-31 21:29:06.654801+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user004 | NULL | 62.247.229.158 | success | 查看设备 | 2025-08-02 09:54:47+00:00 | 95 | 2026-05-31 21:29:06.654802+00:00 | 2026-05-31 21:29:06.654804+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user028 | NULL | 80.55.198.248 | failure | 创建组织 | 2024-09-20 06:07:55+00:00 | 96 | 2026-05-31 21:29:06.654805+00:00 | 2026-05-31 21:29:06.654806+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user029 | NULL | 51.228.9.128 | success | 修改设备 | 2024-11-02 19:50:10+00:00 | 97 | 2026-05-31 21:29:06.654808+00:00 | 2026-05-31 21:29:06.654809+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user019 | NULL | 157.41.215.51 | failure | 查看日志 | 2026-04-03 17:13:58+00:00 | 98 | 2026-05-31 21:29:06.654810+00:00 | 2026-05-31 21:29:06.654812+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user014 | NULL | 165.155.246.63 | success | 查看设备 | 2024-08-16 13:47:57+00:00 | 99 | 2026-05-31 21:29:06.654813+00:00 | 2026-05-31 21:29:06.654815+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |
| user007 | NULL | 70.197.186.245 | success | 修改规则 | 2024-07-02 18:35:52+00:00 | 100 | 2026-05-31 21:29:06.654816+00:00 | 2026-05-31 21:29:06.654817+00:00 | NULL | NULL | NULL | NULL | NULL | NULL |

*（仅显示前100条，共 1237 条）*

---

## organization

**主键**: `id`

**外键**:
- `parent_id` -> `organization.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| name | character varying | NO |  |
| parent_id | bigint | YES |  |
| level | integer | NO |  |
| sort | integer | NO |  |
| code | character varying | YES |  |
| remark | character varying | YES |  |
| id | bigint | NO | nextval('organization_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (2 条)

| name | parent_id | level | sort | code | remark | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 海东公司 | NULL | 1 | 0 | NULL |  | 8 | 2026-05-31 23:28:27.017436+00:00 | 2026-05-31 23:28:27.017444+00:00 | NULL | NULL | NULL |
| 运营部 | 8 | 2 | 0 | NULL |  | 9 | 2026-05-31 23:28:47.326352+00:00 | 2026-05-31 23:28:47.326361+00:00 | NULL | NULL | NULL |

---

## popup_event_limit

**主键**: `id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| device_id | integer | YES |  |
| time_interval_seconds | integer | NO |  |
| response_mode | character varying | NO |  |
| enabled | boolean | NO |  |
| id | bigint | NO | nextval('popup_event_limit_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (20 条)

| device_id | time_interval_seconds | response_mode | enabled | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 5 | ignore | True | 1 | 2026-05-31 21:29:06.699816+00:00 | 2026-05-31 21:29:06.699821+00:00 | NULL | NULL | NULL |
| 2 | 10 | ignore | True | 2 | 2026-05-31 21:29:06.699823+00:00 | 2026-05-31 21:29:06.699825+00:00 | NULL | NULL | NULL |
| 3 | 30 | ignore | False | 3 | 2026-05-31 21:29:06.699827+00:00 | 2026-05-31 21:29:06.699829+00:00 | NULL | NULL | NULL |
| 4 | 0 | delay | True | 4 | 2026-05-31 21:29:06.699831+00:00 | 2026-05-31 21:29:06.699832+00:00 | NULL | NULL | NULL |
| 5 | 5 | delay | True | 5 | 2026-05-31 21:29:06.699834+00:00 | 2026-05-31 21:29:06.699836+00:00 | NULL | NULL | NULL |
| 6 | 10 | delay | True | 6 | 2026-05-31 21:29:06.699838+00:00 | 2026-05-31 21:29:06.699840+00:00 | NULL | NULL | NULL |
| 7 | 0 | immediate | True | 7 | 2026-05-31 21:29:06.699842+00:00 | 2026-05-31 21:29:06.699843+00:00 | NULL | NULL | NULL |
| 8 | 0 | immediate | True | 8 | 2026-05-31 21:29:06.699845+00:00 | 2026-05-31 21:29:06.699847+00:00 | NULL | NULL | NULL |
| 9 | 0 | ignore | True | 9 | 2026-05-31 21:29:06.699849+00:00 | 2026-05-31 21:29:06.699851+00:00 | NULL | NULL | NULL |
| 10 | 60 | delay | False | 10 | 2026-05-31 21:29:06.699852+00:00 | 2026-05-31 21:29:06.699854+00:00 | NULL | NULL | NULL |
| 11 | 60 | immediate | False | 11 | 2026-05-31 21:29:06.699856+00:00 | 2026-05-31 21:29:06.699858+00:00 | NULL | NULL | NULL |
| 12 | 30 | ignore | False | 12 | 2026-05-31 21:29:06.699860+00:00 | 2026-05-31 21:29:06.699861+00:00 | NULL | NULL | NULL |
| 13 | 0 | ignore | False | 13 | 2026-05-31 21:29:06.699863+00:00 | 2026-05-31 21:29:06.699865+00:00 | NULL | NULL | NULL |
| 14 | 5 | immediate | True | 14 | 2026-05-31 21:29:06.699867+00:00 | 2026-05-31 21:29:06.699868+00:00 | NULL | NULL | NULL |
| 15 | 60 | immediate | True | 15 | 2026-05-31 21:29:06.699870+00:00 | 2026-05-31 21:29:06.699872+00:00 | NULL | NULL | NULL |
| 16 | 5 | immediate | True | 16 | 2026-05-31 21:29:06.699874+00:00 | 2026-05-31 21:29:06.699876+00:00 | NULL | NULL | NULL |
| 17 | 0 | immediate | True | 17 | 2026-05-31 21:29:06.699877+00:00 | 2026-05-31 21:29:06.699879+00:00 | NULL | NULL | NULL |
| 18 | 30 | ignore | True | 18 | 2026-05-31 21:29:06.699881+00:00 | 2026-05-31 21:29:06.699883+00:00 | NULL | NULL | NULL |
| 19 | 5 | immediate | True | 19 | 2026-05-31 21:29:06.699885+00:00 | 2026-05-31 21:29:06.699886+00:00 | NULL | NULL | NULL |
| 20 | 5 | delay | True | 20 | 2026-05-31 21:29:06.699888+00:00 | 2026-05-31 21:29:06.699890+00:00 | NULL | NULL | NULL |

---

## popup_setting

**主键**: `id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| config_json | jsonb | NO |  |
| is_active | boolean | NO |  |
| id | bigint | NO | nextval('popup_setting_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (2 条)

| config_json | is_active | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- |
| {'sound': True, 'duration': 5, 'position': 'top... | True | 1 | 2026-05-31 21:29:06.690767+00:00 | 2026-05-31 21:29:06.690772+00:00 | NULL | NULL | NULL |
| {'sound': False, 'duration': 10, 'position': 'b... | False | 2 | 2026-05-31 21:29:06.690774+00:00 | 2026-05-31 21:29:06.690776+00:00 | NULL | NULL | NULL |

---

## preset

**主键**: `id`

**外键**:
- `device_id` -> `device.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| device_id | bigint | NO |  |
| name | character varying | NO |  |
| code | character varying | YES |  |
| p | numeric | YES |  |
| t | numeric | YES |  |
| z | numeric | YES |  |
| time_range_json | jsonb | YES |  |
| id | bigint | NO | nextval('preset_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (0 条)

*(空表)*

---

## pt_weight_file

**主键**: `id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| id | bigint | NO | nextval('pt_weight_file_id_seq'::regclass) |
| name | character varying | NO |  |
| file_path | character varying | NO |  |
| description | character varying | YES |  |
| created_at | timestamp with time zone | NO | now() |
| updated_at | timestamp with time zone | NO | now() |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (0 条)

*(空表)*

---

## push_history

**主键**: `id`

**外键**:
- `device_id` -> `device.id`
- `rule_id` -> `linkage_rule.id`
- `event_type_id` -> `event_type.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| rule_id | bigint | YES |  |
| device_id | bigint | YES |  |
| event_type_id | bigint | YES |  |
| push_channels | jsonb | YES |  |
| push_target | character varying | YES |  |
| push_time | timestamp with time zone | YES |  |
| status | character varying | YES |  |
| retry_count | integer | NO |  |
| operator | character varying | YES |  |
| count | integer | NO |  |
| detail | text | YES |  |
| id | bigint | NO | nextval('push_history_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (0 条)

*(空表)*

---

## region

**主键**: `id`

**外键**:
- `org_id` -> `organization.id`
- `parent_id` -> `region.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| name | character varying | NO |  |
| code | character varying | YES |  |
| parent_id | bigint | YES |  |
| level | integer | NO |  |
| sort | integer | NO |  |
| id | bigint | NO | nextval('region_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |
| org_id | bigint | YES |  |
| remark | character varying | YES |  |

### 数据 (19 条)

| name | code | parent_id | level | sort | id | created_at | updated_at | created_by | updated_by | deleted_at | org_id | remark |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 北京市 | 110000 | NULL | 1 | 1 | 1 | 2026-05-31 21:29:06.081271+00:00 | 2026-05-31 21:29:06.081279+00:00 | NULL | NULL | NULL | NULL | NULL |
| 上海市 | 310000 | NULL | 1 | 2 | 2 | 2026-05-31 21:29:06.081283+00:00 | 2026-05-31 21:29:06.081285+00:00 | NULL | NULL | NULL | NULL | NULL |
| 广东省 | 440000 | NULL | 1 | 3 | 3 | 2026-05-31 21:29:06.081287+00:00 | 2026-05-31 21:29:06.081289+00:00 | NULL | NULL | NULL | NULL | NULL |
| 浙江省 | 330000 | NULL | 1 | 4 | 4 | 2026-05-31 21:29:06.081292+00:00 | 2026-05-31 21:29:06.081294+00:00 | NULL | NULL | NULL | NULL | NULL |
| 江苏省 | 320000 | NULL | 1 | 5 | 5 | 2026-05-31 21:29:06.081296+00:00 | 2026-05-31 21:29:06.081299+00:00 | NULL | NULL | NULL | NULL | NULL |
| 朝阳区 | 110105 | 1 | 2 | 1 | 6 | 2026-05-31 21:29:06.086607+00:00 | 2026-05-31 21:29:06.086613+00:00 | NULL | NULL | NULL | NULL | NULL |
| 海淀区 | 110108 | 1 | 2 | 2 | 7 | 2026-05-31 21:29:06.086617+00:00 | 2026-05-31 21:29:06.086619+00:00 | NULL | NULL | NULL | NULL | NULL |
| 浦东新区 | 310115 | 2 | 2 | 1 | 8 | 2026-05-31 21:29:06.086621+00:00 | 2026-05-31 21:29:06.086624+00:00 | NULL | NULL | NULL | NULL | NULL |
| 徐汇区 | 310104 | 2 | 2 | 2 | 9 | 2026-05-31 21:29:06.086626+00:00 | 2026-05-31 21:29:06.086629+00:00 | NULL | NULL | NULL | NULL | NULL |
| 深圳市 | 440300 | 3 | 2 | 1 | 10 | 2026-05-31 21:29:06.086631+00:00 | 2026-05-31 21:29:06.086633+00:00 | NULL | NULL | NULL | NULL | NULL |
| 广州市 | 440100 | 3 | 2 | 2 | 11 | 2026-05-31 21:29:06.086636+00:00 | 2026-05-31 21:29:06.086638+00:00 | NULL | NULL | NULL | NULL | NULL |
| 杭州市 | 330100 | 4 | 2 | 1 | 12 | 2026-05-31 21:29:06.086641+00:00 | 2026-05-31 21:29:06.086643+00:00 | NULL | NULL | NULL | NULL | NULL |
| 宁波市 | 330200 | 4 | 2 | 2 | 13 | 2026-05-31 21:29:06.086645+00:00 | 2026-05-31 21:29:06.086648+00:00 | NULL | NULL | NULL | NULL | NULL |
| 南京市 | 320100 | 5 | 2 | 1 | 14 | 2026-05-31 21:29:06.086650+00:00 | 2026-05-31 21:29:06.086653+00:00 | NULL | NULL | NULL | NULL | NULL |
| 苏州市 | 320500 | 5 | 2 | 2 | 15 | 2026-05-31 21:29:06.086655+00:00 | 2026-05-31 21:29:06.086658+00:00 | NULL | NULL | NULL | NULL | NULL |
| 大学城南 | s201 | NULL | 1 | 1 | 16 | 2026-05-31 23:31:03.535744+00:00 | 2026-05-31 23:31:03.535752+00:00 | NULL | NULL | NULL | 8 | NULL |
| 南区 | s101 | 16 | 1 | 0 | 17 | 2026-05-31 23:31:21.054207+00:00 | 2026-05-31 23:32:28.277576+00:00 | NULL | NULL | NULL | 8 | NULL |
| 大学城北 | NULL | NULL | 1 | 0 | 18 | 2026-05-31 23:59:53.633434+00:00 | 2026-05-31 23:59:53.633443+00:00 | NULL | NULL | NULL | 8 | NULL |
| 北区 | NULL | 18 | 2 | 0 | 19 | 2026-06-01 00:00:47.425933+00:00 | 2026-06-01 00:00:47.425942+00:00 | NULL | NULL | NULL | 8 | NULL |

---

## resource

**主键**: `id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| resource | character varying | NO |  |
| resource_group | character varying | NO |  |
| method | character varying | NO |  |
| service_code | character varying | YES |  |
| description | character varying | YES |  |
| hidden | boolean | NO |  |
| id | bigint | NO | nextval('resource_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (28 条)

| resource | resource_group | method | service_code | description | hidden | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| /api/v1/device | device | GET | NULL | device GET | False | 1 | 2026-05-31 21:29:05.981560+00:00 | 2026-05-31 21:29:05.981566+00:00 | NULL | NULL | NULL |
| /api/v1/device | device | POST | NULL | device POST | False | 2 | 2026-05-31 21:29:05.981570+00:00 | 2026-05-31 21:29:05.981573+00:00 | NULL | NULL | NULL |
| /api/v1/device | device | PUT | NULL | device PUT | False | 3 | 2026-05-31 21:29:05.981576+00:00 | 2026-05-31 21:29:05.981578+00:00 | NULL | NULL | NULL |
| /api/v1/device | device | DELETE | NULL | device DELETE | False | 4 | 2026-05-31 21:29:05.981581+00:00 | 2026-05-31 21:29:05.981584+00:00 | NULL | NULL | NULL |
| /api/v1/algorithm | algorithm | GET | NULL | algorithm GET | False | 5 | 2026-05-31 21:29:05.981587+00:00 | 2026-05-31 21:29:05.981589+00:00 | NULL | NULL | NULL |
| /api/v1/algorithm | algorithm | POST | NULL | algorithm POST | False | 6 | 2026-05-31 21:29:05.981592+00:00 | 2026-05-31 21:29:05.981595+00:00 | NULL | NULL | NULL |
| /api/v1/algorithm | algorithm | PUT | NULL | algorithm PUT | False | 7 | 2026-05-31 21:29:05.981598+00:00 | 2026-05-31 21:29:05.981600+00:00 | NULL | NULL | NULL |
| /api/v1/algorithm | algorithm | DELETE | NULL | algorithm DELETE | False | 8 | 2026-05-31 21:29:05.981603+00:00 | 2026-05-31 21:29:05.981606+00:00 | NULL | NULL | NULL |
| /api/v1/deployment | deployment | GET | NULL | deployment GET | False | 9 | 2026-05-31 21:29:05.981609+00:00 | 2026-05-31 21:29:05.981611+00:00 | NULL | NULL | NULL |
| /api/v1/deployment | deployment | POST | NULL | deployment POST | False | 10 | 2026-05-31 21:29:05.981614+00:00 | 2026-05-31 21:29:05.981617+00:00 | NULL | NULL | NULL |
| /api/v1/deployment | deployment | PUT | NULL | deployment PUT | False | 11 | 2026-05-31 21:29:05.981620+00:00 | 2026-05-31 21:29:05.981622+00:00 | NULL | NULL | NULL |
| /api/v1/deployment | deployment | DELETE | NULL | deployment DELETE | False | 12 | 2026-05-31 21:29:05.981625+00:00 | 2026-05-31 21:29:05.981628+00:00 | NULL | NULL | NULL |
| /api/v1/linkage | linkage | GET | NULL | linkage GET | False | 13 | 2026-05-31 21:29:05.981631+00:00 | 2026-05-31 21:29:05.981633+00:00 | NULL | NULL | NULL |
| /api/v1/linkage | linkage | POST | NULL | linkage POST | False | 14 | 2026-05-31 21:29:05.981636+00:00 | 2026-05-31 21:29:05.981639+00:00 | NULL | NULL | NULL |
| /api/v1/linkage | linkage | PUT | NULL | linkage PUT | False | 15 | 2026-05-31 21:29:05.981642+00:00 | 2026-05-31 21:29:05.981644+00:00 | NULL | NULL | NULL |
| /api/v1/linkage | linkage | DELETE | NULL | linkage DELETE | False | 16 | 2026-05-31 21:29:05.981647+00:00 | 2026-05-31 21:29:05.981650+00:00 | NULL | NULL | NULL |
| /api/v1/system | system | GET | NULL | system GET | False | 17 | 2026-05-31 21:29:05.981653+00:00 | 2026-05-31 21:29:05.981655+00:00 | NULL | NULL | NULL |
| /api/v1/system | system | POST | NULL | system POST | False | 18 | 2026-05-31 21:29:05.981658+00:00 | 2026-05-31 21:29:05.981661+00:00 | NULL | NULL | NULL |
| /api/v1/system | system | PUT | NULL | system PUT | False | 19 | 2026-05-31 21:29:05.981664+00:00 | 2026-05-31 21:29:05.981666+00:00 | NULL | NULL | NULL |
| /api/v1/system | system | DELETE | NULL | system DELETE | False | 20 | 2026-05-31 21:29:05.981669+00:00 | 2026-05-31 21:29:05.981672+00:00 | NULL | NULL | NULL |
| /api/v1/user | user | GET | NULL | user GET | False | 21 | 2026-05-31 21:29:05.981675+00:00 | 2026-05-31 21:29:05.981677+00:00 | NULL | NULL | NULL |
| /api/v1/user | user | POST | NULL | user POST | False | 22 | 2026-05-31 21:29:05.981680+00:00 | 2026-05-31 21:29:05.981682+00:00 | NULL | NULL | NULL |
| /api/v1/user | user | PUT | NULL | user PUT | False | 23 | 2026-05-31 21:29:05.981685+00:00 | 2026-05-31 21:29:05.981688+00:00 | NULL | NULL | NULL |
| /api/v1/user | user | DELETE | NULL | user DELETE | False | 24 | 2026-05-31 21:29:05.981691+00:00 | 2026-05-31 21:29:05.981693+00:00 | NULL | NULL | NULL |
| /api/v1/monitor | monitor | GET | NULL | monitor GET | False | 25 | 2026-05-31 21:29:05.981697+00:00 | 2026-05-31 21:29:05.981699+00:00 | NULL | NULL | NULL |
| /api/v1/monitor | monitor | POST | NULL | monitor POST | False | 26 | 2026-05-31 21:29:05.981702+00:00 | 2026-05-31 21:29:05.981704+00:00 | NULL | NULL | NULL |
| /api/v1/monitor | monitor | PUT | NULL | monitor PUT | False | 27 | 2026-05-31 21:29:05.981707+00:00 | 2026-05-31 21:29:05.981710+00:00 | NULL | NULL | NULL |
| /api/v1/monitor | monitor | DELETE | NULL | monitor DELETE | False | 28 | 2026-05-31 21:29:05.981713+00:00 | 2026-05-31 21:29:05.981715+00:00 | NULL | NULL | NULL |

---

## role

**主键**: `id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| name | character varying | NO |  |
| code | character varying | YES |  |
| description | character varying | YES |  |
| status | character varying | NO |  |
| id | bigint | NO | nextval('role_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (5 条)

| name | code | description | status | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 超级管理员 | super_admin | 系统最高权限 | active | 1 | 2026-05-31 21:29:05.941830+00:00 | 2026-05-31 21:29:05.941836+00:00 | NULL | NULL | NULL |
| 管理员 | admin | 日常管理权限 | active | 2 | 2026-05-31 21:29:05.941841+00:00 | 2026-05-31 21:29:05.941843+00:00 | NULL | NULL | NULL |
| 普通用户 | user | 查看权限 | active | 4 | 2026-05-31 21:29:05.941852+00:00 | 2026-05-31 21:29:05.941855+00:00 | NULL | NULL | NULL |
| 运维工程师 | ops | 设备运维权限 | active | 3 | 2026-05-31 21:29:05.941847+00:00 | 2026-05-31 23:29:39.235458+00:00 | NULL | NULL | 2026-05-31 23:29:39.232568+00:00 |
| 审计员 | auditor | 日志审计权限 | active | 5 | 2026-05-31 21:29:05.941859+00:00 | 2026-05-31 23:29:50.665356+00:00 | NULL | NULL | 2026-05-31 23:29:50.664626+00:00 |

---

## role_menu

**主键**: `id`

**外键**:
- `role_id` -> `role.id`
- `menu_id` -> `menu.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| role_id | bigint | NO |  |
| menu_id | bigint | NO |  |
| id | bigint | NO | nextval('role_menu_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (25 条)

| role_id | menu_id | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 14 | 1 | 2026-05-31 21:29:06.035578+00:00 | 2026-05-31 21:29:06.035584+00:00 | NULL | NULL | NULL |
| 1 | 19 | 2 | 2026-05-31 21:29:06.035587+00:00 | 2026-05-31 21:29:06.035590+00:00 | NULL | NULL | NULL |
| 1 | 8 | 3 | 2026-05-31 21:29:06.035592+00:00 | 2026-05-31 21:29:06.035594+00:00 | NULL | NULL | NULL |
| 2 | 16 | 4 | 2026-05-31 21:29:06.035597+00:00 | 2026-05-31 21:29:06.035599+00:00 | NULL | NULL | NULL |
| 2 | 2 | 5 | 2026-05-31 21:29:06.035602+00:00 | 2026-05-31 21:29:06.035604+00:00 | NULL | NULL | NULL |
| 2 | 18 | 6 | 2026-05-31 21:29:06.035606+00:00 | 2026-05-31 21:29:06.035609+00:00 | NULL | NULL | NULL |
| 2 | 3 | 7 | 2026-05-31 21:29:06.035611+00:00 | 2026-05-31 21:29:06.035613+00:00 | NULL | NULL | NULL |
| 2 | 5 | 8 | 2026-05-31 21:29:06.035616+00:00 | 2026-05-31 21:29:06.035618+00:00 | NULL | NULL | NULL |
| 3 | 17 | 9 | 2026-05-31 21:29:06.035621+00:00 | 2026-05-31 21:29:06.035623+00:00 | NULL | NULL | NULL |
| 3 | 16 | 10 | 2026-05-31 21:29:06.035625+00:00 | 2026-05-31 21:29:06.035628+00:00 | NULL | NULL | NULL |
| 3 | 8 | 11 | 2026-05-31 21:29:06.035630+00:00 | 2026-05-31 21:29:06.035632+00:00 | NULL | NULL | NULL |
| 3 | 19 | 12 | 2026-05-31 21:29:06.035635+00:00 | 2026-05-31 21:29:06.035637+00:00 | NULL | NULL | NULL |
| 3 | 3 | 13 | 2026-05-31 21:29:06.035640+00:00 | 2026-05-31 21:29:06.035642+00:00 | NULL | NULL | NULL |
| 3 | 11 | 14 | 2026-05-31 21:29:06.035644+00:00 | 2026-05-31 21:29:06.035647+00:00 | NULL | NULL | NULL |
| 3 | 7 | 15 | 2026-05-31 21:29:06.035649+00:00 | 2026-05-31 21:29:06.035651+00:00 | NULL | NULL | NULL |
| 4 | 2 | 16 | 2026-05-31 21:29:06.035654+00:00 | 2026-05-31 21:29:06.035656+00:00 | NULL | NULL | NULL |
| 4 | 1 | 17 | 2026-05-31 21:29:06.035658+00:00 | 2026-05-31 21:29:06.035661+00:00 | NULL | NULL | NULL |
| 4 | 7 | 18 | 2026-05-31 21:29:06.035663+00:00 | 2026-05-31 21:29:06.035666+00:00 | NULL | NULL | NULL |
| 5 | 16 | 19 | 2026-05-31 21:29:06.035668+00:00 | 2026-05-31 21:29:06.035670+00:00 | NULL | NULL | NULL |
| 5 | 12 | 20 | 2026-05-31 21:29:06.035673+00:00 | 2026-05-31 21:29:06.035675+00:00 | NULL | NULL | NULL |
| 5 | 10 | 21 | 2026-05-31 21:29:06.035678+00:00 | 2026-05-31 21:29:06.035680+00:00 | NULL | NULL | NULL |
| 5 | 17 | 22 | 2026-05-31 21:29:06.035682+00:00 | 2026-05-31 21:29:06.035684+00:00 | NULL | NULL | NULL |
| 5 | 15 | 23 | 2026-05-31 21:29:06.035687+00:00 | 2026-05-31 21:29:06.035689+00:00 | NULL | NULL | NULL |
| 5 | 1 | 24 | 2026-05-31 21:29:06.035692+00:00 | 2026-05-31 21:29:06.035694+00:00 | NULL | NULL | NULL |
| 5 | 9 | 25 | 2026-05-31 21:29:06.035696+00:00 | 2026-05-31 21:29:06.035699+00:00 | NULL | NULL | NULL |

---

## role_resource

**主键**: `id`

**外键**:
- `resource_id` -> `resource.id`
- `role_id` -> `role.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| role_id | bigint | NO |  |
| resource_id | bigint | NO |  |
| id | bigint | NO | nextval('role_resource_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (78 条)

| role_id | resource_id | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 17 | 1 | 2026-05-31 21:29:06.053815+00:00 | 2026-05-31 21:29:06.053821+00:00 | NULL | NULL | NULL |
| 1 | 7 | 2 | 2026-05-31 21:29:06.053824+00:00 | 2026-05-31 21:29:06.053827+00:00 | NULL | NULL | NULL |
| 1 | 28 | 3 | 2026-05-31 21:29:06.053829+00:00 | 2026-05-31 21:29:06.053832+00:00 | NULL | NULL | NULL |
| 1 | 25 | 4 | 2026-05-31 21:29:06.053834+00:00 | 2026-05-31 21:29:06.053837+00:00 | NULL | NULL | NULL |
| 1 | 6 | 5 | 2026-05-31 21:29:06.053839+00:00 | 2026-05-31 21:29:06.053841+00:00 | NULL | NULL | NULL |
| 1 | 2 | 6 | 2026-05-31 21:29:06.053844+00:00 | 2026-05-31 21:29:06.053846+00:00 | NULL | NULL | NULL |
| 1 | 5 | 7 | 2026-05-31 21:29:06.053848+00:00 | 2026-05-31 21:29:06.053851+00:00 | NULL | NULL | NULL |
| 2 | 18 | 8 | 2026-05-31 21:29:06.053853+00:00 | 2026-05-31 21:29:06.053855+00:00 | NULL | NULL | NULL |
| 2 | 12 | 9 | 2026-05-31 21:29:06.053858+00:00 | 2026-05-31 21:29:06.053860+00:00 | NULL | NULL | NULL |
| 2 | 28 | 10 | 2026-05-31 21:29:06.053863+00:00 | 2026-05-31 21:29:06.053865+00:00 | NULL | NULL | NULL |
| 2 | 21 | 11 | 2026-05-31 21:29:06.053867+00:00 | 2026-05-31 21:29:06.053870+00:00 | NULL | NULL | NULL |
| 2 | 11 | 12 | 2026-05-31 21:29:06.053872+00:00 | 2026-05-31 21:29:06.053874+00:00 | NULL | NULL | NULL |
| 2 | 7 | 13 | 2026-05-31 21:29:06.053877+00:00 | 2026-05-31 21:29:06.053879+00:00 | NULL | NULL | NULL |
| 2 | 24 | 14 | 2026-05-31 21:29:06.053882+00:00 | 2026-05-31 21:29:06.053884+00:00 | NULL | NULL | NULL |
| 2 | 16 | 15 | 2026-05-31 21:29:06.053886+00:00 | 2026-05-31 21:29:06.053889+00:00 | NULL | NULL | NULL |
| 2 | 3 | 16 | 2026-05-31 21:29:06.053891+00:00 | 2026-05-31 21:29:06.053893+00:00 | NULL | NULL | NULL |
| 2 | 26 | 17 | 2026-05-31 21:29:06.053896+00:00 | 2026-05-31 21:29:06.053898+00:00 | NULL | NULL | NULL |
| 2 | 10 | 18 | 2026-05-31 21:29:06.053901+00:00 | 2026-05-31 21:29:06.053903+00:00 | NULL | NULL | NULL |
| 2 | 15 | 19 | 2026-05-31 21:29:06.053905+00:00 | 2026-05-31 21:29:06.053908+00:00 | NULL | NULL | NULL |
| 2 | 25 | 20 | 2026-05-31 21:29:06.053910+00:00 | 2026-05-31 21:29:06.053912+00:00 | NULL | NULL | NULL |
| 2 | 8 | 21 | 2026-05-31 21:29:06.053915+00:00 | 2026-05-31 21:29:06.053917+00:00 | NULL | NULL | NULL |
| 2 | 4 | 22 | 2026-05-31 21:29:06.053919+00:00 | 2026-05-31 21:29:06.053922+00:00 | NULL | NULL | NULL |
| 2 | 2 | 23 | 2026-05-31 21:29:06.053924+00:00 | 2026-05-31 21:29:06.053926+00:00 | NULL | NULL | NULL |
| 2 | 1 | 24 | 2026-05-31 21:29:06.053929+00:00 | 2026-05-31 21:29:06.053931+00:00 | NULL | NULL | NULL |
| 2 | 22 | 25 | 2026-05-31 21:29:06.053934+00:00 | 2026-05-31 21:29:06.053936+00:00 | NULL | NULL | NULL |
| 2 | 27 | 26 | 2026-05-31 21:29:06.053939+00:00 | 2026-05-31 21:29:06.053941+00:00 | NULL | NULL | NULL |
| 2 | 20 | 27 | 2026-05-31 21:29:06.053943+00:00 | 2026-05-31 21:29:06.053946+00:00 | NULL | NULL | NULL |
| 3 | 22 | 28 | 2026-05-31 21:29:06.053948+00:00 | 2026-05-31 21:29:06.053950+00:00 | NULL | NULL | NULL |
| 3 | 16 | 29 | 2026-05-31 21:29:06.053953+00:00 | 2026-05-31 21:29:06.053955+00:00 | NULL | NULL | NULL |
| 3 | 8 | 30 | 2026-05-31 21:29:06.053958+00:00 | 2026-05-31 21:29:06.053960+00:00 | NULL | NULL | NULL |
| 3 | 17 | 31 | 2026-05-31 21:29:06.053962+00:00 | 2026-05-31 21:29:06.053965+00:00 | NULL | NULL | NULL |
| 3 | 21 | 32 | 2026-05-31 21:29:06.053967+00:00 | 2026-05-31 21:29:06.053969+00:00 | NULL | NULL | NULL |
| 3 | 20 | 33 | 2026-05-31 21:29:06.053972+00:00 | 2026-05-31 21:29:06.053974+00:00 | NULL | NULL | NULL |
| 3 | 2 | 34 | 2026-05-31 21:29:06.053976+00:00 | 2026-05-31 21:29:06.053979+00:00 | NULL | NULL | NULL |
| 3 | 14 | 35 | 2026-05-31 21:29:06.053981+00:00 | 2026-05-31 21:29:06.053983+00:00 | NULL | NULL | NULL |
| 3 | 12 | 36 | 2026-05-31 21:29:06.053986+00:00 | 2026-05-31 21:29:06.053988+00:00 | NULL | NULL | NULL |
| 3 | 15 | 37 | 2026-05-31 21:29:06.053991+00:00 | 2026-05-31 21:29:06.053993+00:00 | NULL | NULL | NULL |
| 3 | 25 | 38 | 2026-05-31 21:29:06.053995+00:00 | 2026-05-31 21:29:06.053998+00:00 | NULL | NULL | NULL |
| 3 | 5 | 39 | 2026-05-31 21:29:06.054000+00:00 | 2026-05-31 21:29:06.054002+00:00 | NULL | NULL | NULL |
| 3 | 24 | 40 | 2026-05-31 21:29:06.054005+00:00 | 2026-05-31 21:29:06.054007+00:00 | NULL | NULL | NULL |
| 3 | 11 | 41 | 2026-05-31 21:29:06.054010+00:00 | 2026-05-31 21:29:06.054012+00:00 | NULL | NULL | NULL |
| 3 | 13 | 42 | 2026-05-31 21:29:06.054014+00:00 | 2026-05-31 21:29:06.054017+00:00 | NULL | NULL | NULL |
| 3 | 9 | 43 | 2026-05-31 21:29:06.054019+00:00 | 2026-05-31 21:29:06.054021+00:00 | NULL | NULL | NULL |
| 3 | 23 | 44 | 2026-05-31 21:29:06.054024+00:00 | 2026-05-31 21:29:06.054026+00:00 | NULL | NULL | NULL |
| 3 | 3 | 45 | 2026-05-31 21:29:06.054029+00:00 | 2026-05-31 21:29:06.054031+00:00 | NULL | NULL | NULL |
| 3 | 27 | 46 | 2026-05-31 21:29:06.054033+00:00 | 2026-05-31 21:29:06.054036+00:00 | NULL | NULL | NULL |
| 3 | 10 | 47 | 2026-05-31 21:29:06.054038+00:00 | 2026-05-31 21:29:06.054040+00:00 | NULL | NULL | NULL |
| 3 | 28 | 48 | 2026-05-31 21:29:06.054043+00:00 | 2026-05-31 21:29:06.054045+00:00 | NULL | NULL | NULL |
| 3 | 1 | 49 | 2026-05-31 21:29:06.054047+00:00 | 2026-05-31 21:29:06.054050+00:00 | NULL | NULL | NULL |
| 3 | 19 | 50 | 2026-05-31 21:29:06.054052+00:00 | 2026-05-31 21:29:06.054055+00:00 | NULL | NULL | NULL |
| 3 | 26 | 51 | 2026-05-31 21:29:06.054057+00:00 | 2026-05-31 21:29:06.054059+00:00 | NULL | NULL | NULL |
| 3 | 7 | 52 | 2026-05-31 21:29:06.054062+00:00 | 2026-05-31 21:29:06.054064+00:00 | NULL | NULL | NULL |
| 3 | 18 | 53 | 2026-05-31 21:29:06.054067+00:00 | 2026-05-31 21:29:06.054069+00:00 | NULL | NULL | NULL |
| 3 | 6 | 54 | 2026-05-31 21:29:06.054072+00:00 | 2026-05-31 21:29:06.054074+00:00 | NULL | NULL | NULL |
| 3 | 4 | 55 | 2026-05-31 21:29:06.054076+00:00 | 2026-05-31 21:29:06.054079+00:00 | NULL | NULL | NULL |
| 4 | 18 | 56 | 2026-05-31 21:29:06.054081+00:00 | 2026-05-31 21:29:06.054083+00:00 | NULL | NULL | NULL |
| 4 | 27 | 57 | 2026-05-31 21:29:06.054086+00:00 | 2026-05-31 21:29:06.054088+00:00 | NULL | NULL | NULL |
| 4 | 19 | 58 | 2026-05-31 21:29:06.054090+00:00 | 2026-05-31 21:29:06.054093+00:00 | NULL | NULL | NULL |
| 4 | 14 | 59 | 2026-05-31 21:29:06.054095+00:00 | 2026-05-31 21:29:06.054097+00:00 | NULL | NULL | NULL |
| 4 | 9 | 60 | 2026-05-31 21:29:06.054100+00:00 | 2026-05-31 21:29:06.054102+00:00 | NULL | NULL | NULL |
| 4 | 3 | 61 | 2026-05-31 21:29:06.054105+00:00 | 2026-05-31 21:29:06.054107+00:00 | NULL | NULL | NULL |
| 4 | 26 | 62 | 2026-05-31 21:29:06.054109+00:00 | 2026-05-31 21:29:06.054112+00:00 | NULL | NULL | NULL |
| 4 | 28 | 63 | 2026-05-31 21:29:06.054114+00:00 | 2026-05-31 21:29:06.054117+00:00 | NULL | NULL | NULL |
| 4 | 11 | 64 | 2026-05-31 21:29:06.054119+00:00 | 2026-05-31 21:29:06.054121+00:00 | NULL | NULL | NULL |
| 4 | 2 | 65 | 2026-05-31 21:29:06.054124+00:00 | 2026-05-31 21:29:06.054126+00:00 | NULL | NULL | NULL |
| 4 | 15 | 66 | 2026-05-31 21:29:06.054129+00:00 | 2026-05-31 21:29:06.054131+00:00 | NULL | NULL | NULL |
| 4 | 17 | 67 | 2026-05-31 21:29:06.054133+00:00 | 2026-05-31 21:29:06.054136+00:00 | NULL | NULL | NULL |
| 4 | 25 | 68 | 2026-05-31 21:29:06.054138+00:00 | 2026-05-31 21:29:06.054140+00:00 | NULL | NULL | NULL |
| 4 | 8 | 69 | 2026-05-31 21:29:06.054143+00:00 | 2026-05-31 21:29:06.054145+00:00 | NULL | NULL | NULL |
| 4 | 10 | 70 | 2026-05-31 21:29:06.054147+00:00 | 2026-05-31 21:29:06.054150+00:00 | NULL | NULL | NULL |
| 4 | 20 | 71 | 2026-05-31 21:29:06.054152+00:00 | 2026-05-31 21:29:06.054154+00:00 | NULL | NULL | NULL |
| 4 | 16 | 72 | 2026-05-31 21:29:06.054157+00:00 | 2026-05-31 21:29:06.054159+00:00 | NULL | NULL | NULL |
| 5 | 8 | 73 | 2026-05-31 21:29:06.054162+00:00 | 2026-05-31 21:29:06.054164+00:00 | NULL | NULL | NULL |
| 5 | 9 | 74 | 2026-05-31 21:29:06.054166+00:00 | 2026-05-31 21:29:06.054169+00:00 | NULL | NULL | NULL |
| 5 | 27 | 75 | 2026-05-31 21:29:06.054171+00:00 | 2026-05-31 21:29:06.054173+00:00 | NULL | NULL | NULL |
| 5 | 25 | 76 | 2026-05-31 21:29:06.054176+00:00 | 2026-05-31 21:29:06.054178+00:00 | NULL | NULL | NULL |
| 5 | 10 | 77 | 2026-05-31 21:29:06.054180+00:00 | 2026-05-31 21:29:06.054183+00:00 | NULL | NULL | NULL |
| 5 | 21 | 78 | 2026-05-31 21:29:06.054185+00:00 | 2026-05-31 21:29:06.054187+00:00 | NULL | NULL | NULL |

---

## task

**主键**: `id`

**外键**:
- `algorithm_id` -> `algorithm.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| task_name | character varying | NO |  |
| trigger_type | character varying | NO |  |
| trigger_rule | character varying | YES |  |
| algorithm_id | bigint | YES |  |
| status | character varying | NO |  |
| last_run_time | timestamp with time zone | YES |  |
| id | bigint | NO | nextval('task_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (15 条)

| task_name | trigger_type | trigger_rule | algorithm_id | status | last_run_time | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 定时任务-01 | interval | 0 0 * * 0 | 1 | active | 2024-08-15 20:30:05+00:00 | 1 | 2026-05-31 21:29:06.504384+00:00 | 2026-05-31 21:29:06.504389+00:00 | NULL | NULL | NULL |
| 定时任务-02 | interval | 0 8,20 * * * | 1 | paused | NULL | 2 | 2026-05-31 21:29:06.504392+00:00 | 2026-05-31 21:29:06.504394+00:00 | NULL | NULL | NULL |
| 定时任务-03 | interval | 0 8,20 * * * | 1 | stopped | NULL | 3 | 2026-05-31 21:29:06.504397+00:00 | 2026-05-31 21:29:06.504399+00:00 | NULL | NULL | NULL |
| 定时任务-04 | cron | 0 0 * * 0 | 1 | stopped | 2025-03-05 05:31:13+00:00 | 4 | 2026-05-31 21:29:06.504401+00:00 | 2026-05-31 21:29:06.504403+00:00 | NULL | NULL | NULL |
| 定时任务-05 | interval | 0 0 * * 0 | 1 | active | NULL | 5 | 2026-05-31 21:29:06.504405+00:00 | 2026-05-31 21:29:06.504407+00:00 | NULL | NULL | NULL |
| 定时任务-06 | cron | 0 8,20 * * * | 1 | active | NULL | 6 | 2026-05-31 21:29:06.504409+00:00 | 2026-05-31 21:29:06.504412+00:00 | NULL | NULL | NULL |
| 定时任务-07 | cron | 0 8,20 * * * | 1 | stopped | 2025-11-27 14:54:52+00:00 | 7 | 2026-05-31 21:29:06.504414+00:00 | 2026-05-31 21:29:06.504416+00:00 | NULL | NULL | NULL |
| 定时任务-08 | cron | */5 * * * * | 1 | stopped | 2024-10-11 06:09:15+00:00 | 8 | 2026-05-31 21:29:06.504418+00:00 | 2026-05-31 21:29:06.504420+00:00 | NULL | NULL | NULL |
| 定时任务-09 | cron | 0 0 * * * | 1 | active | NULL | 9 | 2026-05-31 21:29:06.504422+00:00 | 2026-05-31 21:29:06.504424+00:00 | NULL | NULL | NULL |
| 定时任务-10 | interval | 0 8,20 * * * | 1 | paused | NULL | 10 | 2026-05-31 21:29:06.504426+00:00 | 2026-05-31 21:29:06.504428+00:00 | NULL | NULL | NULL |
| 定时任务-11 | interval | 0 0 * * * | 1 | paused | 2025-03-18 03:39:31+00:00 | 11 | 2026-05-31 21:29:06.504430+00:00 | 2026-05-31 21:29:06.504432+00:00 | NULL | NULL | NULL |
| 定时任务-12 | cron | 0 8,20 * * * | 1 | active | 2025-03-28 17:30:56+00:00 | 12 | 2026-05-31 21:29:06.504434+00:00 | 2026-05-31 21:29:06.504436+00:00 | NULL | NULL | NULL |
| 定时任务-13 | interval | 0 0 * * 0 | 1 | stopped | 2024-11-09 04:51:39+00:00 | 13 | 2026-05-31 21:29:06.504438+00:00 | 2026-05-31 21:29:06.504440+00:00 | NULL | NULL | NULL |
| 定时任务-14 | cron | 0 0 * * * | 1 | active | 2026-02-21 01:35:32+00:00 | 14 | 2026-05-31 21:29:06.504442+00:00 | 2026-05-31 21:29:06.504445+00:00 | NULL | NULL | NULL |
| 定时任务-15 | cron | 0 0 * * 0 | 1 | active | 2026-03-17 04:22:25+00:00 | 15 | 2026-05-31 21:29:06.504447+00:00 | 2026-05-31 21:29:06.504449+00:00 | NULL | NULL | NULL |

---

## task_device

**主键**: `id`

**外键**:
- `task_id` -> `task.id`
- `device_id` -> `device.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| task_id | bigint | NO |  |
| device_id | bigint | NO |  |
| id | bigint | NO | nextval('task_device_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (0 条)

*(空表)*

---

## ui_theme

**主键**: `id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| name | character varying | NO |  |
| platform | character varying | YES |  |
| theme_color | character varying | YES |  |
| logo_url | character varying | YES |  |
| is_active | boolean | NO |  |
| id | bigint | NO | nextval('ui_theme_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (2 条)

| name | platform | theme_color | logo_url | is_active | id | created_at | updated_at | created_by | updated_by | deleted_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 默认主题 | web | #409EFF | /logo.png | True | 1 | 2026-05-31 21:29:06.709742+00:00 | 2026-05-31 21:29:06.709747+00:00 | NULL | NULL | NULL |
| 深色主题 | web | #303133 | /logo-dark.png | False | 2 | 2026-05-31 21:29:06.709749+00:00 | 2026-05-31 21:29:06.709751+00:00 | NULL | NULL | NULL |

---

## user

**主键**: `id`

**外键**:
- `org_id` -> `organization.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| username | character varying | NO |  |
| real_name | character varying | YES |  |
| password | character varying | NO |  |
| avatar | character varying | YES |  |
| phone | character varying | YES |  |
| email | character varying | YES |  |
| gender | character varying | YES |  |
| org_id | bigint | YES |  |
| status | character varying | NO |  |
| id | bigint | NO | nextval('user_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |
| role | character varying | NO | 'user'::character varying |
| employee_id | character varying | YES |  |

### 数据 (1 条)

| username | real_name | password | avatar | phone | email | gender | org_id | status | id | created_at | updated_at | created_by | updated_by | deleted_at | role | employee_id |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zhangsan | 张三 | $2b$12$jkAjRT04FJJTp5v5w7IT5.fyMzlYAVR4QTwNfKQI... | NULL | 1230 | NULL | NULL | 9 | active | 31 | 2026-05-31 23:29:17.798325+00:00 | 2026-05-31 23:29:17.798331+00:00 | NULL | NULL | NULL | user | 1 |

---

## user_role

**主键**: `id`

**外键**:
- `role_id` -> `role.id`
- `user_id` -> `user.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| user_id | bigint | NO |  |
| role_id | bigint | NO |  |
| id | bigint | NO | nextval('user_role_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (0 条)

*(空表)*

---

## video_setting

**主键**: `id`

**外键**:
- `org_id` -> `organization.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| event_types | jsonb | YES |  |
| record_duration_seconds | integer | NO |  |
| status | boolean | NO |  |
| id | bigint | NO | nextval('video_setting_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |
| org_id | integer | NO |  |
| device_ids | jsonb | YES | '[]'::jsonb |

### 数据 (1 条)

| event_types | record_duration_seconds | status | id | created_at | updated_at | created_by | updated_by | deleted_at | org_id | device_ids |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [8, 1, 2, 4, 10, 11, 12] | 10 | True | 4 | 2026-05-31 23:55:49.587894+00:00 | 2026-06-01 00:01:51.013060+00:00 | NULL | NULL | NULL | 8 | [51, 52, 53] |

---

## warning_event

**主键**: `id`

**外键**:
- `rule_id` -> `linkage_rule.id`
- `event_type_id` -> `event_type.id`
- `algorithm_id` -> `algorithm.id`
- `region_id` -> `region.id`
- `org_id` -> `organization.id`
- `device_id` -> `device.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| device_id | bigint | YES |  |
| org_id | bigint | YES |  |
| region_id | bigint | YES |  |
| algorithm_id | bigint | YES |  |
| event_type_id | bigint | YES |  |
| rule_id | bigint | YES |  |
| event_detail | character varying | YES |  |
| process_status | character varying | NO |  |
| is_compliant | boolean | YES |  |
| report_time | timestamp with time zone | YES |  |
| image_url | character varying | YES |  |
| video_url | character varying | YES |  |
| id | bigint | NO | nextval('warning_event_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (0 条)

*(空表)*

---

## warning_event_archive

**主键**: `id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| device_id | integer | YES |  |
| org_id | integer | YES |  |
| region_id | integer | YES |  |
| algorithm_id | integer | YES |  |
| event_type_id | integer | YES |  |
| rule_id | integer | YES |  |
| event_detail | character varying | YES |  |
| process_status | character varying | NO |  |
| is_compliant | boolean | YES |  |
| report_time | timestamp with time zone | YES |  |
| image_url | character varying | YES |  |
| video_url | character varying | YES |  |
| archived_at | timestamp with time zone | NO |  |
| id | bigint | NO | nextval('warning_event_archive_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (0 条)

*(空表)*

---

## warning_event_tag

**主键**: `id`

**外键**:
- `warning_event_id` -> `warning_event.id`
- `dispose_tag_id` -> `dispose_tag.id`

### 字段定义

| 字段名 | 类型 | 可空 | 默认值 |
|--------|------|------|--------|
| warning_event_id | bigint | NO |  |
| dispose_tag_id | bigint | NO |  |
| id | bigint | NO | nextval('warning_event_tag_id_seq'::regclass) |
| created_at | timestamp with time zone | NO |  |
| updated_at | timestamp with time zone | NO |  |
| created_by | bigint | YES |  |
| updated_by | bigint | YES |  |
| deleted_at | timestamp with time zone | YES |  |

### 数据 (0 条)

*(空表)*

---
