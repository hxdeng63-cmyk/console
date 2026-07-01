# Traffic 纯推理 API 服务文档

`api_service/` 是基于 FastAPI 的交通异常检测纯推理服务。它只负责：

- 接收启停/注册请求
- 调度 7 个算法模块在独立子进程中推理
- 通过 HTTP callback 将结果推送给第三方系统
- 通过 HLS 提供实时流播放地址

业务数据（设备、布控记录、事件持久化）全部由调用方/第三方系统管理，本服务不做持久化。服务重启后，任务状态与设备流映射会丢失，调用方需要重新注册/启动。

---

## 目录

- [基础信息](#基础信息)
- [认证](#认证)
- [通用返回格式](#通用返回格式)
- [核心概念](#核心概念)
  - [Deployment 与任务](#deployment-与任务)
  - [Stream ID 与 Device ID](#stream-id-与-device-id)
  - [GPU 分配](#gpu-分配)
  - [静态文件与媒体路径](#静态文件与媒体路径)
- [接口列表](#接口列表)
  - [健康检查](#健康检查)
  - [启动推理任务](#启动推理任务)
  - [查询启动进度](#查询启动进度)
  - [停止推理任务](#停止推理任务)
  - [查询停止进度](#查询停止进度)
  - [查询任务实时状态](#查询任务实时状态)
  - [重启推理任务](#重启推理任务)
  - [批量重启](#批量重启)
  - [注册设备流](#注册设备流)
  - [查询注册进度](#查询注册进度)
  - [获取播放地址](#获取播放地址)
- [Callback 推送格式](#callback-推送格式)
  - [触发条件与频率](#触发条件与频率)
  - [请求头](#请求头)
  - [Payload 字段说明](#payload-字段说明)
  - [Payload 完整示例](#payload-完整示例)
  - [媒体文件路径规则](#媒体文件路径规则)
- [安全机制](#安全机制)
- [环境变量](#环境变量)
- [模块名对照表](#模块名对照表)
- [完整调用示例](#完整调用示例)
- [错误码](#错误码)

---

## 基础信息

- **默认监听地址**：`0.0.0.0:10088`
- **Docker 默认端口**：`127.0.0.1:10000`（仅本机可访问，见 `docs/DOCKER.md`）
- **API 前缀**：`/api/v1`
- **Swagger UI**：`http://<host>:<port>/docs`
- **OpenAPI Schema**：`http://<host>:<port>/openapi.json`

启动服务：

```bash
cd /mnt/home/api/traffic
python -m api_service.main
```

指定端口启动：

```bash
TRAFFIC_API_PORT=10000 python -m api_service.main
```

---

## 认证

默认启用固定 Bearer Token，通过请求头 `Authorization` 传递。

```http
Authorization: Bearer <TRAFFIC_API_AUTH_TOKEN>
```

默认 Token 为 `traffic-api-token-change-me-in-production`，**生产环境务必通过环境变量覆盖**。

开发调试可关闭认证：

```bash
TRAFFIC_API_AUTH_DISABLED=1 python -m api_service.main
```

关闭认证后，所有接口无需携带 `Authorization` 头即可访问。当认证启用时，缺少 Token、Token 错误、或格式不正确均返回 `401 Unauthorized`。

---

## 通用返回格式

### 成功响应

成功响应由具体接口定义，通常为 `200 OK`，返回 JSON 对象。

### 错误响应

错误响应统一为：

```json
{
  "detail": {
    "code": 400,
    "message": "错误描述"
  }
}
```

HTTP 状态码与 `code` 通常一致，常见状态码见 [错误码](#错误码)。

---

## 核心概念

### Deployment 与任务

- 一次 `POST /api/v1/deployments/{id}/start` 调用会在后台启动一个推理子进程，称为一个**任务（task）**。
- 每个 deployment 同时只能有一个活跃任务（`pending`、`running`、`stopping`）。重复启动会返回 `409 Conflict`。
- 任务状态通过 `GET /api/v1/deployments/{id}/start/status/{task_id}` 查询。
- 调用 `POST /api/v1/deployments/{id}/stop` 会停止该 deployment 的活跃任务，并联动停止该 deployment 关联的 HLS 设备流。
- 调用 `POST /api/v1/deployments/{id}/restart` 可在单 deployment 维度先停止再启动；调用 `POST /api/v1/deployments/restart-all` 可批量重启已启动过的 deployment。
- 子进程异常退出时，服务会将状态置为 `crashed`，**不会自动重启**，由调用方通过 `/status` 检测后决定再次 `start` 或调用 `restart`。

### Stream ID 与 Device ID

- `device_id`：`start` 请求 `stream_map` 中的**键（key）**，用于标识一路视频设备，也是标注视频输出目录 `{deployment_id}/{device_id}/` 的组成部分。
- `stream_id`：callback payload、截图目录中的流标识。为避免调用方在 callback 中无法反查 device_id，当前版本强制 `stream_id == str(device_id)`。
- 在 `start` 请求的 `stream_map` 中，`key` 为 `device_id`，`value` 仅作兼容保留，实际会被覆盖为 `str(device_id)`。
- 当前版本一次 `start` 请求只启动一个视频源，因此只取 `stream_map` 的第一个键值对；若 `stream_map` 为空，则默认使用 `deployment_{id}` 同时作为 `stream_id` 和 `device_id`。
- callback payload 中的 `stream_id` 字段**原样回传** `start` 时计算出的值，调用方可按 `stream_id == str(device_id)` 直接匹配。

### GPU 分配

- GPU 列表通过环境变量 `TRAFFIC_API_GPU_DEVICES` 配置，默认 `0,1,2,3`。
- 启动任务时，优先使用请求 `config.gpu_id` 中指定的 GPU；若未指定或指定非法，则按轮询方式分配。
- 子进程通过设置 `CUDA_VISIBLE_DEVICES={gpu_id}` 来绑定 GPU。若 `gpu_id` 为 `cpu` 或 GPU 列表为空，则不设置 CUDA 设备变量，使用 CPU 推理。

### 静态文件与媒体路径

服务会挂载两个静态文件目录：

| 挂载路径 | 物理目录（容器内） | 说明 |
|----------|-------------------|------|
| `/uploads` | `api_service/uploads/` | 截图、标注视频、HLS 文件 |
| `/stream` | `api_service/uploads/stream/` | HLS 播放地址快捷入口 |

Docker 启动时会将宿主机 `./uploads` 挂载到容器的 `/app/api_service/uploads/`，因此媒体文件可在宿主机直接查看。

---

## 接口列表

### 健康检查

```http
GET /api/v1/health
```

**响应示例**：

```json
{
  "code": 200,
  "message": "ok",
  "service": "traffic-api"
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | int | HTTP 状态码，固定 200 |
| `message` | string | 状态描述，固定 "ok" |
| `service` | string | 服务名，固定 "traffic-api" |

---

### 启动推理任务

```http
POST /api/v1/deployments/{id}/start
```

启动指定 `deployment_id` 的推理任务。每路视频流对应一个独立 Python 子进程，GPU 按配置轮询分配。

**Path 参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 布控任务 ID |

**请求体**：

```json
{
  "module_name": "traffic",
  "video_path": "rtsp://admin:pass@192.168.1.100:554/live",
  "stream_map": {
    "1001": "1001"
  },
  "config": {
    "callback_url": "https://third-party.example.com/events",
    "gpu_id": "0",
    "push_interval": 1.0
  }
}
```

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `module_name` | string | 是 | 算法模块名，见 [模块名对照表](#模块名对照表) |
| `video_path` | string | 是 | 视频源路径或 RTSP URL |
| `stream_map` | object | 否 | `device_id -> 兼容占位` 映射；只取第一个 key 作为 `device_id`，`stream_id` 被强制置为 `str(device_id)`；为空时使用默认值 |
| `config` | object | 否 | 算法模块配置，可包含 `callback_url`、`gpu_id`、`push_interval` 等 |

`config` 中常见字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `callback_url` | string | 推理结果回调地址。必须为 `http/https` 公网地址，禁止本地/回环/私有地址（SSRF 防护） |
| `gpu_id` | string | 指定 GPU ID，如 `"0"`。不指定则轮询分配 |
| `push_interval` | float | 最小推送间隔（秒），默认 `1.0` |

**响应示例**（当配置了 `callback_url` 时）：

```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "pending",
  "deployment_id": "42",
  "module_name": "traffic",
  "stream_id": "1001",
  "callback_token": "cbk_7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d"
}
```

**响应字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `task_id` | string | 任务 ID，用于后续查询状态 |
| `status` | string | 固定为 `pending` |
| `deployment_id` | string | 布控任务 ID |
| `module_name` | string | 算法模块名 |
| `stream_id` | string | 实际使用的流标识，等于 `str(device_id)` |
| `callback_token` | string \| null | 当 `callback_url` 存在时返回，callback 推送会带 `Authorization: Bearer <callback_token>`；未配置 callback 时为 `null` |

**常见错误**：

- `400`：`module_name` 为空、不存在，`video_path` 为空，`callback_url` 非法，或 `stream_id`/`device_id` 包含非法字符。
- `409`：同一 deployment 已有活跃任务。
- `503`：当前并发数/单 GPU 并发数/显存不足，服务拒绝启动新任务。
- `500`：子进程启动失败。

---

### 查询启动进度

```http
GET /api/v1/deployments/{id}/start/status/{task_id}
```

**响应示例**：

```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "deployment_id": "42",
  "status": "running",
  "module_name": "traffic",
  "stream_id": "1001",
  "gpu_id": "0",
  "source_path": "rtsp://192.168.1.100:554/live",
  "callback_url": "https://third-party.example.com/events",
  "output_dir": "/app/api_service/uploads/annotations/42/1001",
  "pid": 12345,
  "result": null,
  "created_at": 1715683200.123
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `task_id` | string | 任务 ID |
| `deployment_id` | string | 布控任务 ID |
| `status` | string | 任务状态，见下方状态说明 |
| `module_name` | string | 算法模块名 |
| `stream_id` | string | 流标识 |
| `gpu_id` | string | 分配的 GPU ID |
| `source_path` | string | 视频源路径 |
| `callback_url` | string \| null | 回调地址 |
| `output_dir` | string | 标注视频输出目录 |
| `pid` | int \| null | 子进程 PID |
| `result` | any | 任务完成/失败时的结果，运行中为 `null` |
| `created_at` | float | 任务创建时间戳（秒） |

**任务状态枚举**：

| 状态 | 含义 |
|------|------|
| `pending` | 已提交，等待子进程启动完成 |
| `running` | 子进程已启动，正在推理 |
| `stopping` | 已收到停止请求，正在优雅退出 |
| `completed` | 子进程正常结束（视频播放完或被正常停止） |
| `failed` | 子进程异常退出或停止超时 |

---

### 停止推理任务

```http
POST /api/v1/deployments/{id}/stop
```

停止指定 `deployment_id` 的活跃任务，并联动停止该 deployment 关联的 HLS 设备流。

**响应示例**：

```json
{
  "task_id": "stop-1-42",
  "status": "pending",
  "deployment_id": "42"
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `task_id` | string | 停止任务 ID，用于查询停止进度 |
| `status` | string | 固定为 `pending` |
| `deployment_id` | string | 布控任务 ID |

**常见错误**：

- `404`：该 deployment 没有运行中的任务。

---

### 查询停止进度

```http
GET /api/v1/deployments/{id}/stop/status/{task_id}
```

**响应示例**：

```json
{
  "task_id": "stop-1-42",
  "deployment_id": "42",
  "status": "completed",
  "target_task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "target_status": "completed"
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `task_id` | string | 停止任务 ID |
| `deployment_id` | string | 布控任务 ID |
| `status` | string | `completed` 表示目标任务已停止，`pending` 表示仍在停止中 |
| `target_task_id` | string | 被停止的推理任务 ID |
| `target_status` | string | 目标任务的最终状态 |

---

### 查询任务实时状态

```http
GET /api/v1/deployments/{id}/status
```

返回指定 deployment 当前活跃任务的实时状态，无需 `task_id`。

**响应示例**：

```json
{
  "deployment_id": "42",
  "status": "running",
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "stream_id": "1001",
  "module_name": "traffic",
  "gpu_id": "0",
  "pid": 12345,
  "started_at": 1715683200.123,
  "uptime_seconds": 1234,
  "callback_url": "https://third-party.example.com/events",
  "callback_token": "cbk_7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d"
}
```

**status 枚举**：

| 值 | 含义 |
|---|------|
| `pending` | 已提交但子进程未启动 |
| `running` | 子进程运行中 |
| `stopping` | 收到停止请求，正在退出 |
| `stopped` | 用户主动停止后正常退出 |
| `crashed` | 子进程异常退出（exit_code != 0） |
| `completed` | 视频源结束，进程正常退出（exit_code=0） |

**说明**：

- 子进程异常退出时，服务**不会自动重启**，由调用方检测 `crashed` 后决定调用 `restart` 或 `start`。
- `completed` / `crashed` / `stopped` 状态的任务允许再次调用 `start`，不返回 `409`。

---

### 重启推理任务

```http
POST /api/v1/deployments/{id}/restart
```

对单个 deployment 执行“先 stop，再 start”的重启操作。

**行为**：

- 若该 deployment 当前有活跃任务，先调用 `stop`，等待任务退出后再按原参数启动。
- 若无活跃任务，直接按最近一次 `start` 的参数启动；若从未启动过，返回 `404`。
- 立即返回 `restart_task_id`，异步执行；通过 `GET /api/v1/deployments/{id}/restart/status/{restart_task_id}` 查询进度。
- 重启完成后，`restart/status` 响应中会包含新的推理任务 ID `new_task_id`，可通过 `GET /api/v1/deployments/{id}/start/status/{new_task_id}` 进一步查询推理任务状态。

**响应示例**：

```json
{
  "task_id": "restart-a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "pending",
  "deployment_id": "42"
}
```

**进度查询响应示例**：

```json
{
  "task_id": "restart-a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "deployment_id": "42",
  "status": "completed",
  "new_task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "error": null
}
```

---

### 批量重启

```http
POST /api/v1/deployments/restart-all
```

批量重启所有在**当前服务生命周期内**启动过的 deployment。

**请求体**（可选）：

```json
{
  "deployment_ids": ["42", "43"]
}
```

- 若提供 `deployment_ids`，仅重启列表中的 deployment。
- 若请求体为空，则重启所有已记录 deployment（服务重启后记录丢失）。

**行为**：

- 异步逐个重启，相邻任务间隔 `TRAFFIC_API_STARTUP_STAGGER_SECONDS` 秒（默认 3 秒），避免多子进程同时抢显存。
- 实时推送进度到 `task_id` 状态对象。

**响应示例**：

```json
{
  "task_id": "batch-restart-...",
  "status": "pending"
}
```

**进度查询**：

```http
GET /api/v1/deployments/restart-all/status/{task_id}
```

**响应示例**：

```json
{
  "task_id": "batch-restart-...",
  "status": "completed",
  "total": 3,
  "restarted": 3,
  "failed": 0,
  "skipped": 0,
  "errors": []
}
```

---

### 注册设备流

```http
POST /api/v1/stream/devices/register
```

为设备注册 RTSP 流，后台启动 FFmpeg 将 RTSP 转为 HLS，输出到 `uploads/stream/device_{id}/index.m3u8`。

**请求体（推荐方式）**：

```json
{
  "devices": [
    {
      "device_id": 1001,
      "rtsp_url": "rtsp://admin:pass@192.168.1.100:554/live"
    }
  ]
}
```

**兼容方式**（仅复用已缓存的 RTSP URL）：

```json
{
  "device_ids": [1001, 1002]
}
```

两种字段至少要填一个；同时为空时返回 `400`。`device_ids` 中的设备若未提供 `rtsp_url` 且未在内存中注册过，则会被跳过。

**请求字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `devices` | list[object] | 条件 | 包含 `device_id` 和 `rtsp_url` 的设备列表 |
| `device_ids` | list[int] | 条件 | 兼容前端的设备 ID 列表 |

`devices` 中每项字段：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `device_id` | int \| string | 是 | 设备 ID，仅允许字母、数字、下划线、连字符 |
| `rtsp_url` | string | 是 | RTSP 地址，必须以 `rtsp://` 或 `rtsps://` 开头；本地文件路径也允许 |

**响应示例**：

```json
{
  "task_id": "h1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "pending"
}
```

**常见错误**：

- `400`：`devices` 和 `device_ids` 同时为空，`device_id` 非法，或 `rtsp_url` 协议不支持。

---

### 查询注册进度

```http
GET /api/v1/stream/devices/register/status/{task_id}
```

**响应示例**：

```json
{
  "status": "completed",
  "total": 2,
  "done": 1,
  "failed": 1,
  "pending": 0,
  "results": [
    {
      "device_id": "1001",
      "success": true,
      "flv_url": "/stream/device_1001/index.m3u8",
      "source_type": "stream",
      "stream_name": "device_1001",
      "error": null
    },
    {
      "device_id": "1002",
      "success": false,
      "flv_url": null,
      "source_type": "stream",
      "stream_name": "device_1002",
      "error": "未找到 ffmpeg 可执行文件，请安装 FFmpeg"
    }
  ]
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 注册任务状态，`pending` 或 `completed` |
| `total` | int | 注册设备总数 |
| `done` | int | 成功启动 FFmpeg 的设备数 |
| `failed` | int | 失败的设备数 |
| `pending` | int | 尚未处理的设备数 |
| `results` | list[object] | 每个设备的注册结果 |

`results` 中每项字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `device_id` | string | 设备 ID |
| `success` | bool | 是否成功 |
| `flv_url` | string \| null | HLS 播放相对地址，失败时为 `null` |
| `source_type` | string | 固定为 `"stream"` |
| `stream_name` | string | 流名称，固定为 `device_{device_id}` |
| `error` | string \| null | 失败原因，成功时为 `null` |

---

### 获取播放地址

```http
GET /api/v1/stream/device/{device_id}/flv
```

**响应示例**：

```json
{
  "device_id": 1001,
  "stream_name": "device_1001",
  "flv_url": "/stream/device_1001/index.m3u8",
  "rtsp_url": "rtsp://admin:pass@192.168.1.100:554/live",
  "source_type": "stream"
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `device_id` | int \| string | 设备 ID |
| `stream_name` | string | 流名称 |
| `flv_url` | string | HLS 播放相对地址（字段名沿用前端文档约定） |
| `rtsp_url` | string | 原始 RTSP 地址 |
| `source_type` | string | 固定为 `"stream"` |

**常见错误**：

- `404`：设备流未注册或 FFmpeg 进程已退出。

---

## Callback 推送格式

推理过程中，算法模块会按 `config.callback_url` 将结果以 `POST` 方式推送给第三方系统。

### 回调地址的确定

1. 优先使用 `start` 请求 `config.callback_url` 字段。
2. 若请求中未提供，则使用环境变量 `TRAFFIC_API_DEFAULT_CALLBACK_URL`。
3. 若均未配置，则不推送。

### SSRF 防护

`callback_url` 必须满足：

- 协议为 `http` 或 `https`。
- 禁止指向 `localhost`、`127.0.0.1`、`0.0.0.0`、`::1`。
- 禁止指向私有网段：`10.0.0.0/8`、`172.16.0.0/12`、`192.168.0.0/16`、`169.254.0.0/16`。

不符合上述条件会返回 `400`。

### 触发条件与频率

- 最小推送间隔由 `config.push_interval` 或 `TRAFFIC_API_DEFAULT_PUSH_INTERVAL` 控制，默认 `1.0s`。
- 状态变化时（如 `is_jam`、`flow.total`、逆向、行人闯入、疑似事故、违停等）会强制推送，不受最小间隔限制。

### 请求头

```http
POST {callback_url} HTTP/1.1
Content-Type: application/json
Authorization: Bearer <callback_token>
```

- 当 `start` 请求配置了 `callback_url` 时，服务会为该 deployment 生成独立的 `callback_token`，并通过 `Authorization: Bearer <callback_token>` 推送。
- `callback_token` 在 `POST /deployments/{id}/start` 响应中返回，调用方应保存并在接收端校验。
- 若用户在 `config.headers` 中自定义了 `Authorization`，**以服务生成的 `callback_token` 为准**（覆盖用户自定义值），避免暴露 traffic-api 自身 Token。

### Payload 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `stream_id` | string | 流标识 |
| `frame_num` | int | 当前帧序号 |
| `timestamp` | float | 时间戳（秒，含小数） |
| `datetime` | string | ISO-8601 格式时间字符串，固定为毫秒精度 + 显式时区，如 `2024-05-14T12:00:00.123+00:00` |
| `image_url` | string \| null | 事件截图相对路径 |
| `video_url` | string \| null | 标注视频相对路径 |
| `jam` | object \| null | 交通阻塞信息 |
| `anomaly` | object \| null | 异常停车汇总 |
| `flow` | object \| null | 车流量统计 |
| `vehicle_counts_by_type` | object \| null | 按车型统计的车流量 |
| `reverse` | object \| null | 逆向行驶检测 |
| `pedestrian` | object \| null | 行人闯入检测 |
| `accident` | object \| null | 疑似事故检测 |
| `parking_violation` | object \| null | 违停检测 |
| `vest` | object \| null | 反光衣检测 |
| `smoke` | object \| null | 烟雾检测 |
| `construction_vehicle` | object \| null | 工程车检测 |
| `non_motor_vehicle_intrusion` | object \| null | 非机动车闯入 |
| `emergency_lane_occupation` | object \| null | 应急车道占用 |

### Payload 完整示例

```json
{
  "stream_id": "1001",
  "frame_num": 150,
  "timestamp": 1715683200.123,
  "datetime": "2024-05-14T12:00:00.123+00:00",
  "image_url": "/uploads/snapshots/1001/20240514/1001_jam_150_1715683200123.jpg",
  "video_url": "/uploads/annotations/42/1001/1001_output.mp4",
  "jam": {
    "is_jam": true,
    "confidence": 0.8,
    "stopped_count": 4,
    "total_count": 5,
    "avg_stop_duration": 2.5,
    "confirmation_frames": 15
  },
  "anomaly": {
    "stopped_count": 4,
    "total_count": 5,
    "stopped_ratio": 0.8
  },
  "flow": {
    "up_count": 42,
    "down_count": 38,
    "total": 80,
    "left_this_frame": 1,
    "active_count": 5,
    "class_flows": {
      "0": {"up": 35, "down": 30, "total": 65},
      "1": {"up": 7, "down": 8, "total": 15}
    },
    "class_names": {
      "0": "vehicle",
      "1": "two-wheeler"
    }
  },
  "vehicle_counts_by_type": {
    "vehicle": {"up": 35, "down": 30, "total": 65},
    "two-wheeler": {"up": 7, "down": 8, "total": 15}
  },
  "reverse": {
    "reverse_count": 1,
    "total_count": 5,
    "dominant_direction": "up",
    "confirmation_frames": 32,
    "reverse_track_ids": [10003]
  },
  "pedestrian": {
    "intruding": false,
    "pedestrian_count": 0,
    "continuous_frames": 0,
    "total_intrusion_events": 2
  },
  "accident": {
    "is_accident": true,
    "stopped_count": 2,
    "pedestrian_count": 1,
    "continuous_frames": 18,
    "total_accident_events": 1
  },
  "parking_violation": {
    "is_violation": false,
    "stopped_count": 0,
    "vehicle_ids": []
  },
  "vest": {
    "count": 3,
    "detections": []
  },
  "smoke": null,
  "construction_vehicle": null,
  "non_motor_vehicle_intrusion": null,
  "emergency_lane_occupation": null
}
```

### 媒体文件路径规则

| 类型 | 路径规则 |
|------|----------|
| 事件截图 | `/uploads/snapshots/{stream_id}/{YYYYMMDD}/{filename}.jpg` |
| 标注视频 | `/uploads/annotations/{deployment_id}/{device_id}/{stream_id}_output.mp4` |
| HLS 播放 | `/uploads/stream/device_{device_id}/index.m3u8` 或 `/stream/device_{device_id}/index.m3u8` |

标注视频文件名固定为 `{stream_id}_output.mp4`。播放地址中的 `/stream/device_{id}/index.m3u8` 会自动映射到 `/uploads/stream/device_{id}/index.m3u8`。

### Callback 推送失败重试语义

- 当前实现**不缓存失败数据**，单次推送失败不重试，依赖下一帧的 `push_interval` 周期再次推送。
- 推送失败不会暂停子进程；子进程继续推理并在下一周期尝试推送。
- 失败累计次数可在 `GET /api/v1/deployments/{id}/status` 的 `callback_error_count` 字段查看（如实现）。
- 若用户后端长时间不可用，建议通过 `status` 接口监控 `callback_error_count` 并在必要时调用 `stop`。

### stream_map 多设备扩展说明

- **当前版本一次 `start` 请求仅支持一路视频源**，`stream_map` 中只取第一个 `device_id`。
- 多路并发需求请**多次调用 `start`**，每次使用不同的 `deployment_id` 或同一 `deployment_id` 在任务结束后复用。
- 未来版本若支持多路，callback payload 仍通过顶层 `stream_id` 区分，HLS 地址会扩展为数组返回；当前接口保持不变以兼容现有调用方。

---

## 安全机制

- **固定 Bearer Token**：生产环境通过 `TRAFFIC_API_AUTH_TOKEN` 覆盖默认 Token。
- **SSRF 防护**：`callback_url` 禁止指向本地、回环和私有网段。
- **路径穿越防护**：`deployment_id`、`device_id`、`stream_id` 仅允许字母、数字、下划线、连字符、点、冒号、斜杠，且不能包含 `..`。
- **无业务数据持久化**：服务不连接数据库，重启后状态丢失。
- **每路流独立进程**：单个流崩溃不会影响其他流。

---

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `TRAFFIC_API_HOST` | 监听地址 | `0.0.0.0` |
| `TRAFFIC_API_PORT` | 监听端口 | `10088` |
| `TRAFFIC_API_AUTH_TOKEN` | 服务自身 Bearer Token | `traffic-api-token-change-me-in-production` |
| `TRAFFIC_API_AUTH_DISABLED` | 是否关闭认证（`1` 表示关闭） | `0` |
| `TRAFFIC_API_GPU_DEVICES` | GPU 轮询列表，逗号分隔；设为空则仅 CPU | `0,1,2,3` |
| `TRAFFIC_API_MAX_CONCURRENT_DEPLOYMENTS` | 全局最大并发 deployment 数，超出返回 `503` | `8` |
| `TRAFFIC_API_MAX_CONCURRENT_PER_GPU` | 单 GPU 最大并发任务数，超出返回 `503` | `9` |
| `TRAFFIC_API_MIN_GPU_MEMORY_MB` | 单 GPU 最低可用显存要求（MB），显存不足时返回 `503` | `3072` |
| `TRAFFIC_API_STARTUP_STAGGER_SECONDS` | 批量启动/重启时间隔（秒），避免同时 fork 抢显存 | `3.0` |
| `TRAFFIC_API_UPLOADS_DIR` | 静态文件根目录 | `api_service/uploads` |
| `TRAFFIC_API_LOGS_DIR` | 日志目录 | `api_service/logs` |
| `TRAFFIC_API_DEFAULT_CALLBACK_URL` | 默认 callback 地址 | 无 |
| `TRAFFIC_API_DEFAULT_PUSH_INTERVAL` | 默认最小推送间隔（秒） | `1.0` |

### 并发与显存说明

- 上述阈值在 `start` 时校验，任一条件不满足即返回 `503 Service Unavailable`，**不会阻塞等待**。
- 单 GPU 并发按该 GPU 上 `running` / `pending` 任务数计算。
- 显存检查依赖 `pynvml`；若 `pynvml` 不可用或该 GPU 无法查询，则跳过显存检查，仅按并发数限制。
- 30 路并发示例：每张 GPU 并发上限 9，4 张 GPU 可同时承载 36 路；同时需保证每张 GPU 剩余显存 ≥ 3072 MB。

---

## 模块名对照表

| module_name | 兼容别名 | 说明 |
|-------------|----------|------|
| `traffic` | `traffic_jam` | 交通阻塞 / 异常停车 / 摩托车闯入 |
| `vehicle_counting` | — | 车流量统计 |
| `reverse` | `reverse_detection` | 逆向行驶检测 |
| `pedestrian` | `pedestrian_intrusion` | 行人闯入检测 |
| `accident` | `accident_detection` | 疑似事故检测 |
| `vest` | `vest_detection` | 反光衣检测 |
| `fire_smoke` | `fire_smoke_detection` | 火灾 / 烟雾检测 |

接口同时接受**主名称**与**兼容别名**，内部指向同一算法模块。推荐调用方使用主名称。

---

## 完整调用示例

### 1. 启动推理并接收 callback

```bash
TOKEN="traffic-api-token-change-me-in-production"

# 启动任务
# stream_map 中 key 为 device_id，value 会被覆盖为 str(device_id)
curl -X POST "http://127.0.0.1:10000/api/v1/deployments/42/start" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "module_name": "traffic",
    "video_path": "rtsp://192.168.1.100:554/live",
    "stream_map": {"1001": "1001"},
    "config": {
      "callback_url": "https://your-backend.example.com/events",
      "gpu_id": "0"
    }
  }'

# 查询启动状态
curl "http://127.0.0.1:10000/api/v1/deployments/42/start/status/{task_id}" \
  -H "Authorization: Bearer $TOKEN"

# 查询实时状态（无需 task_id）
curl "http://127.0.0.1:10000/api/v1/deployments/42/status" \
  -H "Authorization: Bearer $TOKEN"

# 重启任务
curl -X POST "http://127.0.0.1:10000/api/v1/deployments/42/restart" \
  -H "Authorization: Bearer $TOKEN"

# 查询重启进度
curl "http://127.0.0.1:10000/api/v1/deployments/42/restart/status/{restart_task_id}" \
  -H "Authorization: Bearer $TOKEN"

# 批量重启
curl -X POST "http://127.0.0.1:10000/api/v1/deployments/restart-all" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"deployment_ids": ["42", "43"]}'

# 停止任务
curl -X POST "http://127.0.0.1:10000/api/v1/deployments/42/stop" \
  -H "Authorization: Bearer $TOKEN"

# 查询停止进度
curl "http://127.0.0.1:10000/api/v1/deployments/42/stop/status/{stop_task_id}" \
  -H "Authorization: Bearer $TOKEN"
```

### 2. 注册实时流并播放

```bash
# 注册设备流
curl -X POST "http://127.0.0.1:10000/api/v1/stream/devices/register" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {"device_id": 1001, "rtsp_url": "rtsp://192.168.1.100:554/live"}
    ]
  }'

# 查询注册进度
curl "http://127.0.0.1:10000/api/v1/stream/devices/register/status/{task_id}" \
  -H "Authorization: Bearer $TOKEN"

# 获取播放地址
curl "http://127.0.0.1:10000/api/v1/stream/device/1001/flv" \
  -H "Authorization: Bearer $TOKEN"
```

前端播放器可直接使用返回的 `flv_url`（例如 `/stream/device_1001/index.m3u8`）播放 HLS 流。

---

## 错误码

| HTTP 状态码 | 含义 | 常见场景 |
|-------------|------|----------|
| 200 | 成功 | 正常返回 |
| 400 | 请求参数错误 | 模块名不存在、`callback_url` 非法、stream_id 非法、空注册请求、rtsp_url 协议不支持 |
| 401 | 认证失败 | 缺少 Token、Token 错误、认证未关闭 |
| 404 | 资源不存在 | 任务/注册任务/设备流不存在 |
| 409 | 冲突 | 同一 deployment 已有活跃任务（`pending`/`running`/`stopping`） |
| 503 | 服务暂时不可用 | 并发数/单 GPU 并发数/显存不足，无法启动新任务 |
| 500 | 服务器内部错误 | 子进程启动失败、FFmpeg 未安装 |

---

## 本地测试

启动服务后运行集成测试：

```bash
# 终端 1：启动服务（关闭认证便于调试）
TRAFFIC_API_AUTH_DISABLED=1 TRAFFIC_API_PORT=10000 python -m api_service.main

# 终端 2：运行测试
python -m pytest api_service/tests/ -q --tb=short
```

最新验证结果：

```text
40 passed in 33.12s
```
