# 数据库表与功能模块差距分析

## 数据库表清单（按字母排序）

| 表名 | 行数 | 备注 |
|------|------|------|
| access_platform | 1 | 接入平台表（GB28181/ONVIF/RTSP/RTMP） |
| algorithm | 1 | 算法表 |
| algorithm_service | 1 | 算法服务表 |
| annotation | 1 | 标注表（监测区域/非监测区） |
| clean_record | 1 | 清理记录表 |
| deployment | 1 | 布控任务表 |
| deployment_device | 1 | 布控-设备关联表 |
| deployment_schedule | 1 | 布控时间计划表 |
| device | 1 | 设备表 |
| device_group | 1 | 设备分组表 |
| device_group_membership | 1 | 设备分组-设备关联表 |
| device_stream | 1 | 设备流表 |
| dispose_tag | 1 | 处置标签表 |
| event_type | 1 | 事件类型表 |
| file | 1 | 文件表（录像/截图） |
| firmware | 1 | 固件表 |
| gb28181_device | 1 | GB28181设备扩展表 |
| license | 1 | 许可证表 |
| linkage_rule | 1 | 联动规则表 |
| linkage_rule_device | 1 | 联动规则-设备关联表 |
| menu | 1 | 菜单表 |
| microservice | 1 | 微服务表 |
| onvif_device | 1 | ONVIF设备扩展表 |
| operation_log | 1 | 操作日志表 |
| organization | 1 | 组织表 |
| popup_event_limit | 1 | 弹窗事件限频表 |
| popup_setting | 1 | 弹窗设置表 |
| preset | 1 | 预置点表 |
| push_history | 1 | 推送历史表 |
| region | 1 | 区域表 |
| resource | 1 | 资源表（API权限） |
| role | 1 | 角色表 |
| role_menu | 1 | 角色-菜单关联表 |
| role_resource | 1 | 角色-资源关联表 |
| task | 1 | 任务表 |
| task_device | 1 | 任务-设备关联表 |
| ui_theme | 1 | UI主题表 |
| user | 1 | 用户表 |
| user_role | 1 | 用户-角色关联表 |
| video_setting | 1 | 视频设置表 |

**说明**：所有表均只有1行占位数据，数据库处于初始种子状态。

---

## 前端视图清单

| 视图路径 | 功能描述 | 调用的API/数据源 |
|----------|----------|-----------------|
| super-admin/MenuManage.vue | 菜单管理 | 静态Mock数据 |
| super-admin/ResourceManage.vue | 资源管理 | 静态Mock数据 |
| super-admin/Microservice.vue | 微服务管理 | 静态Mock数据 |
| super-admin/UICustomize.vue | UI定制 | 静态Mock数据 |
| super-admin/LicenseFile.vue | 许可证管理 | 静态Mock数据 |
| user-center/UserManage.vue | 用户管理 | 静态Mock数据 |
| user-center/RoleManage.vue | 角色管理 | 静态Mock数据 |
| user-center/OrgManage.vue | 组织管理 | 静态Mock数据 |
| user-center/OperationHistory.vue | 操作历史 | 静态Mock数据 |
| device/DataSource.vue | 数据源管理 | 静态Mock数据 |
| device/Region.vue | 区域管理 | 静态Mock数据 |
| device/DeviceGroup.vue | 设备分组 | 静态Mock数据 |
| device/access/PlatformList.vue | 接入平台列表 | 静态Mock数据 |
| device/access/Gb28181.vue | GB28181接入 | **静态硬编码数据，无API调用** |
| device/access/Onvif.vue | ONVIF接入 | **静态硬编码数据，无API调用** |
| linkage/TaskEdit.vue | 任务编辑 | 静态Mock数据 |
| linkage/LinkageRule.vue | 联动规则 | **getLinkageRules/createLinkageRule/updateLinkageRule/deleteLinkageRule/enableLinkageRule/disableLinkageRule** |
| linkage/PushHistory.vue | 推送历史 | 静态Mock数据 |
| algorithm/AlgorithmManage.vue | 算法管理 | 静态Mock数据 |
| algorithm/AlgorithmService.vue | 算法服务 | 静态Mock数据 |
| system/VideoSetting.vue | 视频设置 | 静态Mock数据 |
| system/FileManager.vue | 文件管理 | 静态Mock数据 |
| system/PopupSetting.vue | 弹窗设置 | 静态Mock数据 |
| system/DisposeTag.vue | 处置标签 | 静态Mock数据 |
| deployment/Deployment.vue | 布控管理 | **Mock数据（deployments/algorithms/services），无真实API** |
| deployment/Annotation.vue | 标注管理 | **Mock数据（annotations/tags/deployments），无真实API** |
| monitor/MonitorWall.vue | 监控墙 | 静态Mock数据 |
| monitor/FileAnalysis.vue | 文件分析 | 静态Mock数据 |
| monitor/MonitorSingle.vue | 单个监控 | 静态Mock数据 |
| Events.vue | 事件中心 | 静态Mock数据 |
| event-stats/EventStats.vue | 事件统计 | 静态Mock数据 |
| DataClean.vue | 数据清理 | 静态Mock数据 |
| Firmware.vue | 固件管理 | 静态Mock数据 |
| Profile.vue | 个人中心 | 静态Mock数据 |
| Login.vue | 登录页 | 静态Mock数据 |
| Console.vue | 控制台 | 静态Mock数据 |
| MenuPanel.vue | 菜单面板 | 静态Mock数据 |

---

## Gap分析（按视图）

### 视图：deployment/Deployment.vue
- **当前数据源**：Mock数据（`@/mock/deployment/data`）
- **调用的Mock数据**：`deployments`（布控列表）、`algorithms`（算法列表）、`services`（服务列表）
- **API端点**：无（但后端 `linkage_rules.py` 提供了 `/deployments/schedule` 路由）
- **缺失的真实API**：
  - `GET /api/v1/deployments` - 获取布控列表
  - `POST /api/v1/deployments` - 创建布控
  - `PUT /api/v1/deployments/{id}` - 更新布控
  - `DELETE /api/v1/deployments/{id}` - 删除布控
  - `GET /api/v1/algorithms` - 获取算法列表（存在）
  - `GET /api/v1/algorithm-services` - 获取服务列表（存在）
- **状态**：数据缺失 - 视图使用Mock数据，无法与后端联调

---

### 视图：deployment/Annotation.vue
- **当前数据源**：Mock数据（`@/mock/deployment/annotation`）
- **调用的Mock数据**：`annotations`（标注列表）、`tags`（标签列表）、`deployments`（布控列表）
- **API端点**：无真实API调用
- **缺失的真实API**：
  - `GET /api/v1/annotations` - 获取标注列表
  - `POST /api/v1/annotations` - 创建标注
  - `PUT /api/v1/annotations/{id}` - 更新标注
  - `DELETE /api/v1/annotations/{id}` - 删除标注
  - `GET /api/v1/annotations/presets` - 获取预置点
  - `POST /api/v1/annotations/presets` - 创建预置点
- **数据库表**：annotation表（1行）、preset表（1行）已有结构
- **状态**：数据缺失 - 视图完全使用Mock，无API集成

---

### 视图：device/access/Gb28181.vue
- **当前数据源**：**静态硬编码数据**（内联在Vue组件中）
- **调用的Mock数据**：无，使用内联静态数组
- **问题**：
  - 平台列表（platformList）和设备列表（deviceList）均为内联静态数据
  - SIP服务器配置（sipForm）也是本地响应式变量
  - 没有任何API调用
- **缺失的真实API**：
  - `GET /api/v1/access-platforms` - 获取接入平台列表
  - `POST /api/v1/access-platforms` - 创建接入平台
  - `PUT /api/v1/access-platforms/{id}` - 更新接入平台
  - `DELETE /api/v1/access-platforms/{id}` - 删除接入平台
  - `POST /api/v1/access-platforms/{id}/sync` - 同步平台设备
  - `GET /api/v1/devices` - 获取设备列表
  - SIP服务器配置API（目前无对应端点）
- **数据库表**：`access_platform`表（1行）、`gb28181_device`表（1行）已有结构
- **状态**：字段不匹配 + 数据缺失 - SIP配置没有对应数据库表，GB28181设备管理使用硬编码数据

---

### 视图：device/access/Onvif.vue
- **当前数据源**：**静态硬编码数据**（内联在Vue组件中）
- **调用的Mock数据**：无，使用内联静态数组
- **问题**：
  - 设备列表（tableData）为内联静态数据
  - 搜索功能为前端过滤，无真实搜索API
- **缺失的真实API**：
  - `GET /api/v1/devices?access_type=onvif` - 获取ONVIF设备列表
  - `POST /api/v1/devices` - 创建设备
  - `PUT /api/v1/devices/{id}` - 更新设备
  - `DELETE /api/v1/devices/{id}` - 删除设备
  - ONVIF设备发现/搜索API（目前无对应端点）
- **数据库表**：`device`表（1行）、`onvif_device`表（1行）已有结构
- **状态**：字段不匹配 - device表有`access_type='onvif'`约束，但前端设备数据未与后端关联

---

### 视图：linkage/LinkageRule.vue
- **当前数据源**：**真实API调用**
- **调用的API**：
  - `getLinkageRules()` → `GET /api/v1/linkage-rules`
  - `createLinkageRule()` → `POST /api/v1/linkage-rules`
  - `updateLinkageRule()` → `PUT /api/v1/linkage-rules/{id}`
  - `deleteLinkageRule()` → `DELETE /api/v1/linkage-rules/{id}`
  - `enableLinkageRule()` / `disableLinkageRule()` → 状态切换
- **状态**：正常 - API与视图已对接

---

### 视图：device/DeviceGroup.vue
- **当前数据源**：Mock数据（`@/mock/device/deviceGroups.js`）
- **调用的Mock数据**：`deviceGroupList`
- **缺失的真实API**：
  - `GET /api/v1/device-groups` - 获取设备分组
  - `POST /api/v1/device-groups` - 创建分组
  - `PUT /api/v1/device-groups/{id}` - 更新分组
  - `DELETE /api/v1/device-groups/{id}` - 删除分组
  - `GET /api/v1/device-groups/tree` - 获取分组树
- **数据库表**：`device_group`表（1行）、`device_group_membership`表（1行）已有结构
- **状态**：数据缺失 - 视图使用Mock数据

---

### 视图：linkage/PushHistory.vue
- **当前数据源**：Mock数据（`@/mock/linkage/pushHistory.js`）
- **调用的Mock数据**：`pushHistoryList`
- **缺失的真实API**：
  - `GET /api/v1/push-history` - 获取推送历史（后端无此端点）
- **数据库表**：`push_history`表（1行）已有结构，但无对应API
- **状态**：API缺失 - 数据库表存在但无后端API

---

### 视图：algorithm/AlgorithmService.vue
- **当前数据源**：Mock数据（`@/mock/algorithm/services.js`）
- **调用的Mock数据**：`serviceList`
- **缺失的真实API**：
  - `GET /api/v1/algorithm-services` - 获取算法服务（存在）
  - `POST /api/v1/algorithm-services` - 创建服务（存在）
  - `PUT /api/v1/algorithm-services/{id}` - 更新服务（存在）
  - `DELETE /api/v1/algorithm-services/{id}` - 删除服务（存在）
  - `POST /api/v1/algorithm-services/{id}/start` - 启动服务（存在）
  - `POST /api/v1/algorithm-services/{id}/stop` - 停止服务（存在）
  - `POST /api/v1/algorithm-services/{id}/restart` - 重启服务（存在）
  - `GET /api/v1/algorithm-services/{id}/stats` - 获取统计（存在）
- **状态**：API已实现，但视图未集成

---

### 视图：monitor/MonitorWall.vue
- **当前数据源**：Mock数据（`@/mock/monitor/data`）
- **调用的Mock数据**：`deviceTreeData`
- **缺失的真实API**：
  - `GET /api/v1/devices` - 获取设备列表（存在但未使用）
  - `GET /api/v1/device-streams` - 获取设备流（存在但未使用）
- **状态**：数据缺失 - 视图使用Mock数据

---

### 视图：system/VideoSetting.vue
- **当前数据源**：Mock数据（`@/mock/system/videoSettings.js`）
- **调用的Mock数据**：`videoSettingList`
- **缺失的真实API**：
  - `GET /api/v1/video-settings` - 获取视频设置（存在）
  - `POST /api/v1/video-settings` - 创建视频设置（存在）
  - `PUT /api/v1/video-settings/{id}` - 更新视频设置（存在）
  - `DELETE /api/v1/video-settings/{id}` - 删除视频设置（存在）
  - `PUT /api/v1/video-settings/{id}/status` - 更新状态（存在）
- **数据库表**：`video_setting`表（1行）已有结构
- **状态**：API已实现，但视图未集成

---

### 视图：system/PopupSetting.vue
- **当前数据源**：Mock数据（`@/mock/system/popupSettings.js`）
- **调用的Mock数据**：`popupSetting`
- **缺失的真实API**：
  - `GET /api/v1/popup-settings` - 获取弹窗设置（存在）
  - `POST /api/v1/popup-settings` - 创建弹窗设置（存在）
  - `PUT /api/v1/popup-settings/{id}` - 更新弹窗设置（存在）
  - `DELETE /api/v1/popup-settings/{id}` - 删除弹窗设置（存在）
- **数据库表**：`popup_setting`表（1行）、`popup_event_limit`表（1行）已有结构
- **状态**：API已实现，但视图未集成

---

### 视图：system/DisposeTag.vue
- **当前数据源**：Mock数据（`@/mock/system/disposeTags.js`）
- **调用的Mock数据**：`disposeTagList`
- **缺失的真实API**：
  - `GET /api/v1/dispose-tags` - 获取处置标签（存在）
  - `POST /api/v1/dispose-tags` - 创建处置标签（存在）
  - `PUT /api/v1/dispose-tags/{id}` - 更新处置标签（存在）
  - `DELETE /api/v1/dispose-tags/{id}` - 删除处置标签（存在）
- **数据库表**：`dispose_tag`表（1行）、`warning_event_tag`表（1行）已有结构
- **状态**：API已实现，但视图未集成

---

### 视图：system/FileManager.vue
- **当前数据源**：Mock数据（`@/mock/system/files.js`）
- **调用的Mock数据**：`fileList`
- **缺失的真实API**：
  - `GET /api/v1/file-records` - 获取文件列表（存在）
  - `POST /api/v1/file-records` - 创建文件记录（存在）
  - `PUT /api/v1/file-records/{id}` - 更新文件记录（存在）
  - `DELETE /api/v1/file-records/{id}` - 删除文件记录（存在）
  - `POST /api/v1/file-records/{id}/download` - 下载文件（存在）
- **数据库表**：`file`表（1行）已有结构
- **状态**：API已实现，但视图未集成

---

### 视图：DataClean.vue
- **当前数据源**：Mock数据（`@/mock/dataClean/cleanRecords.js`）
- **调用的Mock数据**：`cleanRecordList`
- **缺失的真实API**：
  - 数据清理相关API（目前无对应端点，但`clean_record`表存在）
- **数据库表**：`clean_record`表（1行）已有结构，但无对应API
- **状态**：API缺失 - 数据库表存在但无后端API

---

## 后端API vs 数据库表对照

| API模块 | 对应数据库表 | API路由前缀 | 状态 |
|---------|------------|-----------|------|
| algorithms | algorithm | /api/v1/algorithms | 已实现 |
| algorithm_services | algorithm_service | /api/v1/algorithm-services | 已实现 |
| annotations | annotation, preset | /api/v1/annotations | 已实现 |
| access_platforms | access_platform | /api/v1/access-platforms | 已实现 |
| devices | device | /api/v1/devices | 已实现 |
| device_groups | device_group | /api/v1/device-groups | 已实现 |
| device_streams | device_stream | /api/v1/device-streams | 已实现 |
| dispose_tags | dispose_tag | /api/v1/dispose-tags | 已实现 |
| event_types | event_type | /api/v1/event-types | 已实现 |
| firmware | firmware | /api/v1/firmware | 已实现 |
| file_records | file | /api/v1/file-records | 已实现 |
| linkage_rules | linkage_rule | /api/v1/linkage-rules | 已实现 |
| menus | menu | /api/v1/menus | 已实现 |
| organizations | organization | /api/v1/organizations | 已实现 |
| popup_settings | popup_setting | /api/v1/popup-settings | 已实现 |
| regions | region | /api/v1/regions | 已实现 |
| resources | resource | /api/v1/resources | 已实现 |
| roles | role | /api/v1/roles | 已实现 |
| tasks | task | /api/v1/tasks | 已实现 |
| ui_themes | ui_theme | /api/v1/ui-themes | 已实现 |
| users | user | /api/v1/users | 已实现 |
| video_settings | video_setting | /api/v1/video-settings | 已实现 |
| deployments | deployment, deployment_device, deployment_schedule | /api/v1/linkage-rules/deployments | **路由已实现但前端未调用** |
| push_history | push_history | 无 | **缺失API** |
| clean_record | clean_record | 无 | **缺失API** |
| gb28181_device | gb28181_device | 无独立API | **缺失API（由access_platforms代理）** |
| onvif_device | onvif_device | 无独立API | **缺失API（由devices代理）** |

---

## 总结

### 按问题类型分类

#### 1. 字段不匹配（Field Mismatch）
- **Gb28181.vue**：前端显示`platformNo`、`gbDeviceNo`、`transport`等字段，但`access_platform`表为通用平台表，GB28181特定字段在`gb28181_device`表，两个表需要JOIN查询
- **Onvif.vue**：前端设备包含`deviceModel`、`vendor`等字段，但这些存储在`onvif_device`扩展表，需要关联查询

#### 2. 数据缺失（Data Missing）
- **Deployment.vue**：使用Mock数据，需要API集成
- **Annotation.vue**：使用Mock数据，需要API集成
- **DeviceGroup.vue**：使用Mock数据，需要API集成
- **MonitorWall.vue**：使用Mock数据，需要API集成

#### 3. API已实现但前端未集成
- **AlgorithmService.vue** - 后端API全实现，前端用Mock
- **VideoSetting.vue** - 后端API全实现，前端用Mock
- **PopupSetting.vue** - 后端API全实现，前端用Mock
- **DisposeTag.vue** - 后端API全实现，前端用Mock
- **FileManager.vue** - 后端API全实现，前端用Mock

#### 4. 完全缺失的后端API
- **push_history**：表存在但无API端点
- **clean_record**：表存在但无API端点
- **SIP服务器配置**：无对应表和API（Gb28181.vue需要）

#### 5. 硬编码静态数据的视图
- **Gb28181.vue**：平台列表和设备列表完全硬编码
- **Onvif.vue**：设备列表完全硬编码

### 优先修复建议

1. **高优先级**：Deployment.vue 和 Annotation.vue - 核心业务功能
2. **中优先级**：Gb28181.vue 和 Onvif.vue - 设备接入功能
3. **低优先级**：其他使用Mock的视图（已有API，只需替换数据源）
