/**
 * AI Console API 接口注解
 * 包含 6 个新模块的 API 接口定义
 */

/**
 * @module monitor 实时监控模块
 */

/**
 * 获取设备树列表
 * GET /api/monitor/devices
 * @response { code: number, data: Array<{ id: string, name: string, parentId: string, type: string, status: string, roadName: string, kilometer: string, direction: string }> }
 */
export interface MonitorDevicesResponse {
  code: number
  data: Array<{
    id: string
    name: string
    parentId: string
    type: string
    status: string
    roadName: string
    kilometer: string
    direction: string
  }>
}

/**
 * 获取设备视频流地址
 * GET /api/monitor/video/:deviceId
 * @param deviceId - 设备ID
 * @response { code: number, data: { flvUrl: string, hlsUrl: string, bandwidth: string, osdText: string } }
 */
export interface MonitorVideoResponse {
  code: number
  data: {
    flvUrl: string
    hlsUrl: string
    bandwidth: string
    osdText: string
  }
}

/**
 * 获取实时报警列表
 * GET /api/monitor/alarms
 * @param type - 报警类型（可选）
 * @response { code: number, data: Array<{ id: string, deviceId: string, deviceName: string, eventType: string, isCompliant: boolean, imageUrl: string, thumbnailUrl: string, location: string, captureTime: string }> }
 */
export interface MonitorAlarmsResponse {
  code: number
  data: Array<{
    id: string
    deviceId: string
    deviceName: string
    eventType: string
    isCompliant: boolean
    imageUrl: string
    thumbnailUrl: string
    location: string
    captureTime: string
  }>
}

/**
 * WebSocket 实时报警推送（预留）
 * WS /ws/monitor/alarms
 * @future
 * @response { type: 'alarm', data: { id: string, deviceId: string, deviceName: string, eventType: string, isCompliant: boolean, imageUrl: string, thumbnailUrl: string, location: string, captureTime: string } }
 */
export interface WsMonitorAlarmsMessage {
  type: 'alarm'
  data: {
    id: string
    deviceId: string
    deviceName: string
    eventType: string
    isCompliant: boolean
    imageUrl: string
    thumbnailUrl: string
    location: string
    captureTime: string
  }
}

/**
 * @module eventStats 事件统计模块
 */

/**
 * 获取事件统计汇总
 * GET /api/event-stats/summary
 * @param roadId - 道路ID
 * @param startTime - 开始时间
 * @param endTime - 结束时间
 * @param timeDimension - 时间维度
 * @response { code: number, data: { totalEvents: number, todayEvents: number, eventTypes: Array<{ type: string, count: number }> } }
 */
export interface EventStatsSummaryResponse {
  code: number
  data: {
    totalEvents: number
    todayEvents: number
    eventTypes: Array<{
      type: string
      count: number
    }>
  }
}

/**
 * 获取事件趋势数据
 * GET /api/event-stats/trend
 * @param roadId - 道路ID
 * @param startTime - 开始时间
 * @param endTime - 结束时间
 * @param eventType - 事件类型
 * @response { code: number, data: Array<{ time: string, value: number }> }
 */
export interface EventStatsTrendResponse {
  code: number
  data: Array<{
    time: string
    value: number
  }>
}

/**
 * @module eventManage 事件管理模块
 */

/**
 * 获取事件列表
 * GET /api/event-manage/list
 * @param page - 页码
 * @param pageSize - 每页数量
 * @param deviceId - 设备ID
 * @param orgId - 组织ID
 * @param regionId - 区域ID
 * @param algorithmType - 算法类型
 * @param eventType - 事件类型
 * @param isCompliant - 是否合规
 * @param disposalStatus - 处置状态
 * @param startTime - 开始时间
 * @param endTime - 结束时间
 * @response { code: number, data: { list: Array<any>, total: number } }
 */
export interface EventManageListResponse {
  code: number
  data: {
    list: Array<any>
    total: number
  }
}

/**
 * 获取事件详情
 * GET /api/event-manage/detail/:id
 * @response { code: number, data: any }
 */
export interface EventManageDetailResponse {
  code: number
  data: any
}

/**
 * 处置事件
 * POST /api/event-manage/dispose
 * @param eventId - 事件ID
 * @param disposalType - 处置类型
 * @param disposalNote - 处置备注
 * @response { code: number, message: string }
 */
export interface EventManageDisposeRequest {
  eventId: string
  disposalType: string
  disposalNote: string
}

export interface EventManageDisposeResponse {
  code: number
  message: string
}

/**
 * 导出事件
 * POST /api/event-manage/export
 * @param filters - 筛选条件
 * @response { code: number, data: { downloadUrl: string } }
 */
export interface EventManageExportRequest {
  filters?: Record<string, any>
}

export interface EventManageExportResponse {
  code: number
  data: {
    downloadUrl: string
  }
}

/**
 * @module deployment 布控管理模块
 */

/**
 * 获取布控任务列表
 * GET /api/deployment/list
 * @response { code: number, data: Array<{ id: string, name: string, deviceIds: string[], algorithmId: string, serviceId: string, schedule: string, status: string, createTime: string }> }
 */
export interface DeploymentListResponse {
  code: number
  data: Array<{
    id: string
    name: string
    deviceIds: string[]
    algorithmId: string
    serviceId: string
    schedule: string
    status: string
    createTime: string
  }>
}

/**
 * 创建布控任务
 * POST /api/deployment
 * @param name - 布控任务名称
 * @param algorithmId - 算法ID
 * @param serviceId - 服务ID
 * @param deviceIds - 设备ID列表
 * @param schedule - 调度配置
 * @response { code: number, data: { id: string } }
 */
export interface DeploymentCreateRequest {
  name: string
  algorithmId: string
  serviceId: string
  deviceIds: string[]
  schedule: string
}

export interface DeploymentCreateResponse {
  code: number
  data: {
    id: string
  }
}

/**
 * 更新布控任务
 * PUT /api/deployment/:id
 * @param id - 布控任务ID
 * @param name - 布控任务名称
 * @param algorithmId - 算法ID
 * @param serviceId - 服务ID
 * @param deviceIds - 设备ID列表
 * @param schedule - 调度配置
 * @param status - 状态
 * @response { code: number }
 */
export interface DeploymentUpdateRequest {
  name?: string
  algorithmId?: string
  serviceId?: string
  deviceIds?: string[]
  schedule?: string
  status?: string
}

export interface DeploymentUpdateResponse {
  code: number
}

/**
 * 删除布控任务
 * DELETE /api/deployment/:id
 * @response { code: number }
 */
export interface DeploymentDeleteResponse {
  code: number
}

/**
 * 获取算法列表
 * GET /api/deployment/algorithms
 * @response { code: number, data: Array<any> }
 */
export interface DeploymentAlgorithmsResponse {
  code: number
  data: Array<any>
}

/**
 * 获取服务列表
 * GET /api/deployment/services
 * @response { code: number, data: Array<{ id: string, name: string, address: string }> }
 */
export interface DeploymentServicesResponse {
  code: number
  data: Array<{
    id: string
    name: string
    address: string
  }>
}

/**
 * @module annotation 标注管理模块
 */

/**
 * 获取标注列表
 * GET /api/annotation/list
 * @param deploymentId - 布控任务ID
 * @param deviceId - 设备ID
 * @response { code: number, data: Array<any> }
 */
export interface AnnotationListResponse {
  code: number
  data: Array<any>
}

/**
 * 保存标注
 * POST /api/annotation
 * @param deploymentId - 布控任务ID
 * @param deviceId - 设备ID
 * @param frameImage - 帧图片
 * @param annotations - 标注数据
 * @response { code: number, data: { id: string } }
 */
export interface AnnotationSaveRequest {
  deploymentId: string
  deviceId: string
  frameImage: string
  annotations: Array<any>
}

export interface AnnotationSaveResponse {
  code: number
  data: {
    id: string
  }
}

/**
 * 获取预置点列表
 * GET /api/annotation/presets
 * @param deviceId - 设备ID
 * @response { code: number, data: Array<{ id: string, name: string, p: number, t: number, z: number, timeRange: string }> }
 */
export interface AnnotationPresetsResponse {
  code: number
  data: Array<{
    id: string
    name: string
    p: number
    t: number
    z: number
    timeRange: string
  }>
}

/**
 * 保存预置点
 * POST /api/annotation/presets
 * @param deviceId - 设备ID
 * @param presetId - 预置点ID
 * @param name - 预置点名称
 * @param p - 水平角度
 * @param t - 垂直角度
 * @param z - 缩放
 * @param timeRange - 时间范围
 * @response { code: number }
 */
export interface AnnotationPresetsSaveRequest {
  deviceId: string
  presetId?: string
  name: string
  p: number
  t: number
  z: number
  timeRange?: string
}

export interface AnnotationPresetsSaveResponse {
  code: number
}

/**
 * @module fileAnalysis 文件分析模块
 */

/**
 * 获取设备列表（用于文件分析）
 * GET /api/file-analysis/devices
 * @response 同设备树接口
 */
export type FileAnalysisDevicesResponse = MonitorDevicesResponse

/**
 * 获取录像文件列表
 * GET /api/file-analysis/files
 * @param deviceId - 设备ID
 * @param startTime - 开始时间
 * @param endTime - 结束时间
 * @response { code: number, data: Array<{ id: string, deviceId: string, fileName: string, startTime: string, endTime: string, duration: number }> }
 */
export interface FileAnalysisFilesResponse {
  code: number
  data: Array<{
    id: string
    deviceId: string
    fileName: string
    startTime: string
    endTime: string
    duration: number
  }>
}

/**
 * 获取录像播放地址
 * GET /api/file-analysis/video/:fileId
 * @param fileId - 文件ID
 * @response { code: number, data: { hlsUrl: string, duration: number } }
 */
export interface FileAnalysisVideoResponse {
  code: number
  data: {
    hlsUrl: string
    duration: number
  }
}
