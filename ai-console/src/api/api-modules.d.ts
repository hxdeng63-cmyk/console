// Type declarations for JS API modules to satisfy TypeScript strict mode
// Auto-generated — covers all src/api/*.js exports

declare module '@/api/algorithm-events' {
  export const getAlgorithmEvents: (params?: any) => Promise<any>
  export const getAlgorithmEvent: (id: any) => Promise<any>
  export const handleAlgorithmEvent: (id: any, data: any) => Promise<any>
  export const batchHandleAlgorithmEvents: (data: any) => Promise<any>
  export const getAlgorithmEventStats: () => Promise<any>
  export const exportAlgorithmEvents: (params?: any) => Promise<any>
}

declare module '@/api/algorithms' {
  export const getAlgorithms: (params?: any) => Promise<any>
  export const getAlgorithm: (id: any) => Promise<any>
  export const createAlgorithm: (data: any) => Promise<any>
  export const updateAlgorithm: (id: any, data: any) => Promise<any>
  export const deleteAlgorithm: (id: any) => Promise<any>
  export const deployAlgorithm: (id: any, data: any) => Promise<any>
  export const undeployAlgorithm: (id: any) => Promise<any>
  export const getAlgorithmVersions: (id: any, params?: any) => Promise<any>
}

declare module '@/api/algorithm-services' {
  export const getAlgorithmServices: (params?: any) => Promise<any>
  export const getAlgorithmService: (id: any) => Promise<any>
  export const createAlgorithmService: (data: any) => Promise<any>
  export const updateAlgorithmService: (id: any, data: any) => Promise<any>
  export const deleteAlgorithmService: (id: any) => Promise<any>
  export const startAlgorithmService: (id: any) => Promise<any>
  export const stopAlgorithmService: (id: any) => Promise<any>
  export const restartAlgorithmService: (id: any) => Promise<any>
  export const getAlgorithmServiceStats: (id: any) => Promise<any>
  export const getAlgorithmServiceLogs: (id: any, params?: any) => Promise<any>
}

declare module '@/api/annotations' {
  export const getAnnotations: (params?: any) => Promise<any>
  export const getAnnotation: (id: any) => Promise<any>
  export const createAnnotation: (data: any) => Promise<any>
  export const updateAnnotation: (id: any, data: any) => Promise<any>
  export const deleteAnnotation: (id: any) => Promise<any>
  export const getPresets: (params?: any) => Promise<any>
  export const createPreset: (data: any) => Promise<any>
  export const updatePreset: (id: any, data: any) => Promise<any>
  export const deletePreset: (id: any) => Promise<any>
}

declare module '@/api/auth' {
  export const login: (data: any) => Promise<any>
  export const logout: () => Promise<any>
  export const refreshToken: (data: any) => Promise<any>
  export const getMe: () => Promise<any>
  export const updatePassword: (data: any) => Promise<any>
  export const getSessions: () => Promise<any>
  export const revokeSession: (id: any) => Promise<any>
  export const revokeAllSessions: () => Promise<any>
}

declare module '@/api/cleanRecords' {
  export const getCleanRecords: (params?: any) => Promise<any>
  export const getCleanRecord: (id: any) => Promise<any>
  export const createCleanRecord: (data: any) => Promise<any>
  export const updateCleanRecord: (id: any, data: any) => Promise<any>
  export const deleteCleanRecord: (id: any) => Promise<any>
  export const executeCleanRecord: (data: any) => Promise<any>
  export const executeCleanRecordAsync: (data: any) => Promise<any>
  export const getCleanStatus: (id: any) => Promise<any>
  export const getExecuteCleanRecordStatus: (taskId: any) => Promise<any>
}

declare module '@/api/cleanupPolicy' {
  export const getCleanupPolicy: () => Promise<any>
  export const updateCleanupPolicy: (data: any) => Promise<any>
}

declare module '@/api/data-sources' {
  export const getDataSources: (params?: any) => Promise<any>
  export const getDataSource: (id: any) => Promise<any>
  export const createDataSource: (data: any) => Promise<any>
  export const updateDataSource: (id: any, data: any) => Promise<any>
  export const deleteDataSource: (id: any) => Promise<any>
  export const testConnection: (data: any) => Promise<any>
  export const syncDataSource: (id: any) => Promise<any>
  export const getDataSourceDevices: (id: any, params?: any) => Promise<any>
}

declare module '@/api/deployment' {
  export const deploymentApi: {
    list: (params?: any) => Promise<any>
    get: (id: any) => Promise<any>
    create: (data: any) => Promise<any>
    update: (id: any, data: any) => Promise<any>
    delete: (id: any) => Promise<any>
    restartAll: () => Promise<any>
    getRestartAllStatus: (taskId: any) => Promise<any>
    start: (id: any, data: any) => Promise<any>
    startStatus: (id: any, taskId: any) => Promise<any>
    listAlgorithms: (params?: any) => Promise<any>
    listServices: (params?: any) => Promise<any>
    listDevices: (params?: any) => Promise<any>
  }
}

declare module '@/api/deployments' {
  export const getDeployments: (params?: any) => Promise<any>
  export const getDeployment: (id: any) => Promise<any>
  export const createDeployment: (data: any) => Promise<any>
  export const updateDeployment: (id: any, data: any) => Promise<any>
  export const deleteDeployment: (id: any) => Promise<any>
  export const scaleDeployment: (id: any, data: any) => Promise<any>
  export const restartDeployment: (id: any) => Promise<any>
  export const getDeploymentPods: (id: any, params?: any) => Promise<any>
  export const getDeploymentLogs: (id: any, params?: any) => Promise<any>
  export const updateDeploymentAnnotations: (id: any, data: any) => Promise<any>
}

declare module '@/api/device-groups' {
  export const getDeviceGroups: (params?: any) => Promise<any>
  export const getDeviceGroup: (id: any) => Promise<any>
  export const createDeviceGroup: (data: any) => Promise<any>
  export const updateDeviceGroup: (id: any, data: any) => Promise<any>
  export const deleteDeviceGroup: (id: any) => Promise<any>
  export const getDeviceGroupTree: () => Promise<any>
  export const getDeviceGroupDevices: (id: any, params?: any) => Promise<any>
  export const addDeviceGroupDevices: (id: any, data: any) => Promise<any>
  export const removeDeviceGroupDevices: (id: any, data: any) => Promise<any>
}

declare module '@/api/devices' {
  export const getDevices: (params?: any) => Promise<any>
  export const getDevice: (id: any) => Promise<any>
  export const createDevice: (data: any) => Promise<any>
  export const updateDevice: (id: any, data: any) => Promise<any>
  export const patchDevice: (id: any, data: any) => Promise<any>
  export const deleteDevice: (id: any) => Promise<any>
  export const getDeviceStats: (id: any) => Promise<any>
  export const authorizeDevice: (id: any, data: any) => Promise<any>
  export const revokeDeviceAuth: (id: any) => Promise<any>
  export const getDeviceVideoSources: (id: any, params?: any) => Promise<any>
  export const batchDeleteDevices: (data: any) => Promise<any>
  export const batchUpdateDevices: (data: any) => Promise<any>
  export const exportDevices: (params?: any) => Promise<any>
}

declare module '@/api/event-types' {
  export const getEventTypes: (params?: any) => Promise<any>
  export const getEventType: (id: any) => Promise<any>
  export const createEventType: (data: any) => Promise<any>
  export const updateEventType: (id: any, data: any) => Promise<any>
  export const deleteEventType: (id: any) => Promise<any>
}

declare module '@/api/event-types.js' {
  export const getEventTypes: (params?: any) => Promise<any>
  export const getEventType: (id: any) => Promise<any>
  export const createEventType: (data: any) => Promise<any>
  export const updateEventType: (id: any, data: any) => Promise<any>
  export const deleteEventType: (id: any) => Promise<any>
}

declare module '@/api/event-stats' {
  export const getTodayStats: (params?: any) => Promise<any>
  export const getViolationStats: (params?: any) => Promise<any>
  export const getAlgorithmSummary: (params?: any) => Promise<any>
  export const getSceneStats: (params?: any) => Promise<any>
  export const getTrendStats: (params?: any) => Promise<any>
  export const getEventTrendStats: (params?: any) => Promise<any>
}

declare module '@/api/files' {
  export const getFiles: (params?: any) => Promise<any>
  export const getFile: (id: any) => Promise<any>
  export const uploadFile: (data: any) => Promise<any>
  export const deleteFile: (id: any) => Promise<any>
  export const downloadFile: (id: any, filename?: string) => Promise<any>
  export const getFileUrl: (id: any) => Promise<any>
  export const batchDeleteFiles: (data: any) => Promise<any>
  export const getFileTree: (params?: any) => Promise<any>
}

declare module '@/api/firmwares' {
  export const getFirmwares: (params?: any) => Promise<any>
  export const getFirmware: (id: any) => Promise<any>
  export const uploadFirmware: (data: any) => Promise<any>
  export const deleteFirmware: (id: any) => Promise<any>
  export const upgradeDevice: (id: any, data: any) => Promise<any>
  export const batchUpgradeDevices: (data: any) => Promise<any>
  export const getFirmwareVersions: (deviceType?: string) => Promise<any>
}

declare module '@/api/help' {
  export const getHelpArticles: (params?: any) => Promise<any>
  export const getHelpArticle: (id: any) => Promise<any>
  export const createHelpArticle: (data: any) => Promise<any>
  export const updateHelpArticle: (id: any, data: any) => Promise<any>
  export const deleteHelpArticle: (id: any) => Promise<any>
  export const getHelpCategories: () => Promise<any>
  export const searchHelp: (keyword: string) => Promise<any>
}

declare module '@/api/index' {
  interface ApiRequest {
    get: (url: string, config?: any) => Promise<any>
    post: (url: string, data?: any, config?: any) => Promise<any>
    put: (url: string, data?: any, config?: any) => Promise<any>
    patch: (url: string, data?: any, config?: any) => Promise<any>
    delete: (url: string, config?: any) => Promise<any>
  }
  const request: ApiRequest
  export default request
}

declare module '@/api/index.js' {
  interface ApiRequest {
    get: (url: string, config?: any) => Promise<any>
    post: (url: string, data?: any, config?: any) => Promise<any>
    put: (url: string, data?: any, config?: any) => Promise<any>
    patch: (url: string, data?: any, config?: any) => Promise<any>
    delete: (url: string, config?: any) => Promise<any>
  }
  const request: ApiRequest
  export default request
}

declare module '@/api/licenses' {
  export const getLicenses: (params?: any) => Promise<any>
  export const getLicense: (id: any) => Promise<any>
  export const uploadLicense: (data: any) => Promise<any>
  export const deleteLicense: (id: any) => Promise<any>
  export const getLicenseInfo: () => Promise<any>
  export const verifyLicense: (data: any) => Promise<any>
}

declare module '@/api/linkage-histories' {
  export const getLinkageHistories: (params?: any) => Promise<any>
  export const getLinkageHistory: (id: any) => Promise<any>
  export const exportLinkageHistories: (params?: any) => Promise<any>
}

declare module '@/api/linkage-rules' {
  export const getLinkageRules: (params?: any) => Promise<any>
  export const getLinkageRule: (id: any) => Promise<any>
  export const createLinkageRule: (data: any) => Promise<any>
  export const updateLinkageRule: (id: any, data: any) => Promise<any>
  export const deleteLinkageRule: (id: any) => Promise<any>
  export const enableLinkageRule: (id: any) => Promise<any>
  export const disableLinkageRule: (id: any) => Promise<any>
  export const testLinkageRule: (id: any, data: any) => Promise<any>
  export const copyLinkageRule: (id: any) => Promise<any>
}

declare module '@/api/menus' {
  export const getMenus: () => Promise<any>
  export const getMenu: (id: any) => Promise<any>
  export const createMenu: (data: any) => Promise<any>
  export const updateMenu: (id: any, data: any) => Promise<any>
  export const deleteMenu: (id: any) => Promise<any>
  export const getMenuTree: () => Promise<any>
  export const getMenuButtons: (id: any) => Promise<any>
  export const updateMenuButtons: (id: any, data: any) => Promise<any>
}

declare module '@/api/notifications' {
  export const getNotifications: (params?: any) => Promise<any>
  export const getNotification: (id: any) => Promise<any>
  export const createNotification: (data: any) => Promise<any>
  export const updateNotification: (id: any, data: any) => Promise<any>
  export const deleteNotification: (id: any) => Promise<any>
  export const markAsRead: (id: any) => Promise<any>
  export const markAllAsRead: () => Promise<any>
  export const deleteAllNotifications: () => Promise<any>
}

declare module '@/api/operation-logs' {
  export const getOperationLogs: (params?: any) => Promise<any>
  export const getOperationLog: (id: any) => Promise<any>
  export const exportOperationLogs: (params?: any) => Promise<any>
  export const deleteOperationLog: (id: any) => Promise<any>
  export const deleteOperationLogs: (data: any) => Promise<any>
}

declare module '@/api/operation-logs.js' {
  export const getOperationLogs: (params?: any) => Promise<any>
  export const getOperationLog: (id: any) => Promise<any>
  export const exportOperationLogs: (params?: any) => Promise<any>
  export const deleteOperationLog: (id: any) => Promise<any>
  export const deleteOperationLogs: (data: any) => Promise<any>
}

declare module '@/api/orgs' {
  export const getOrgs: (params?: any) => Promise<any>
  export const getOrg: (id: any) => Promise<any>
  export const createOrg: (data: any) => Promise<any>
  export const updateOrg: (id: any, data: any) => Promise<any>
  export const deleteOrg: (id: any) => Promise<any>
  export const getOrgTree: () => Promise<any>
  export const getOrgUsers: (id: any, params?: any) => Promise<any>
  export const addOrgUsers: (id: any, data: any) => Promise<any>
  export const removeOrgUsers: (id: any, data: any) => Promise<any>
}

declare module '@/api/platforms' {
  export const getPlatforms: (params?: any) => Promise<any>
  export const getPlatform: (id: any) => Promise<any>
  export const createPlatform: (data: any) => Promise<any>
  export const updatePlatform: (id: any, data: any) => Promise<any>
  export const deletePlatform: (id: any) => Promise<any>
  export const syncPlatform: (id: any) => Promise<any>
  export const getPlatformDevices: (id: any, params?: any) => Promise<any>
}

declare module '@/api/popup-settings' {
  export const getPopupSettings: () => Promise<any>
  export const createPopupSetting: (data: any) => Promise<any>
  export const updatePopupSetting: (id: any, data: any) => Promise<any>
  export const deletePopupSetting: (id: any) => Promise<any>
}

declare module '@/api/regions' {
  export const getRegions: (params?: any) => Promise<any>
  export const getRegion: (id: any) => Promise<any>
  export const createRegion: (data: any) => Promise<any>
  export const updateRegion: (id: any, data: any) => Promise<any>
  export const deleteRegion: (id: any) => Promise<any>
  export const getRegionTree: () => Promise<any>
  export const getFullRegionTree: () => Promise<any>
  export const getRegionDevices: (id: any, params?: any) => Promise<any>
}

declare module '@/api/resources' {
  export const getResources: (params?: any) => Promise<any>
  export const getResource: (id: any) => Promise<any>
  export const createResource: (data: any) => Promise<any>
  export const updateResource: (id: any, data: any) => Promise<any>
  export const deleteResource: (id: any) => Promise<any>
  export const getResourceTree: () => Promise<any>
  export const getResourceButtons: (id: any) => Promise<any>
  export const updateResourceButtons: (id: any, data: any) => Promise<any>
}

declare module '@/api/stream' {
  export const registerDevicesAsync: (deviceIds: any[]) => Promise<any>
  export const getRegisterDevicesStatus: (taskId: any) => Promise<any>
  export const getDeviceFlvUrl: (deviceId: any) => Promise<any>
}

declare module '@/api/roles' {
  export const getRoles: (params?: any) => Promise<any>
  export const getRole: (id: any) => Promise<any>
  export const createRole: (data: any) => Promise<any>
  export const updateRole: (id: any, data: any) => Promise<any>
  export const deleteRole: (id: any) => Promise<any>
  export const getRoleMenus: (id: any) => Promise<any>
  export const setRoleMenus: (id: any, data: any) => Promise<any>
  export const getRoleResources: (id: any) => Promise<any>
  export const setRoleResources: (id: any, data: any) => Promise<any>
}

declare module '@/api/sessions' {
  export const getSessions: (params?: any) => Promise<any>
  export const getSession: (id: any) => Promise<any>
  export const deleteSession: (id: any) => Promise<any>
  export const deleteAllSessions: () => Promise<any>
  export const updateSession: (id: any, data: any) => Promise<any>
}

declare module '@/api/system-settings' {
  export const getSystemSettings: () => Promise<any>
  export const updateSystemSettings: (data: any) => Promise<any>
  export const getSystemSetting: (key: any) => Promise<any>
  export const updateSystemSetting: (key: any, data: any) => Promise<any>
  export const resetSystemSettings: () => Promise<any>
}

declare module '@/api/users' {
  export const getUsers: (params?: any) => Promise<any>
  export const getUser: (id: any) => Promise<any>
  export const createUser: (data: any) => Promise<any>
  export const updateUser: (id: any, data: any) => Promise<any>
  export const deleteUser: (id: any) => Promise<any>
  export const getUserRoles: (id: any) => Promise<any>
  export const setUserRoles: (id: any, data: any) => Promise<any>
  export const getUserPermissions: (id: any) => Promise<any>
  export const resetUserPassword: (id: any) => Promise<any>
  export const batchDeleteUsers: (data: any) => Promise<any>
  export const batchUpdateUsers: (data: any) => Promise<any>
}

declare module '@/api/warning-events' {
  export const getList: (params?: any) => Promise<any>
}

declare module '@/api/microservices' {
  export const getMicroservices: (params?: any) => Promise<any>
  export const getMicroservice: (id: any) => Promise<any>
  export const createMicroservice: (data: any) => Promise<any>
  export const updateMicroservice: (id: any, data: any) => Promise<any>
  export const deleteMicroservice: (id: any) => Promise<any>
}

declare module '@/api/ui-themes' {
  export const getUIThemes: (params?: any) => Promise<any>
  export const getUITheme: (id: any) => Promise<any>
  export const createUITheme: (data: any) => Promise<any>
  export const updateUITheme: (id: any, data: any) => Promise<any>
  export const deleteUITheme: (id: any) => Promise<any>
  export const activateUITheme: (id: any) => Promise<any>
}

declare module '@/api/microservices.js' {
  export const getMicroservices: (params?: any) => Promise<any>
  export const getMicroservice: (id: any) => Promise<any>
  export const createMicroservice: (data: any) => Promise<any>
  export const updateMicroservice: (id: any, data: any) => Promise<any>
  export const deleteMicroservice: (id: any) => Promise<any>
}

declare module '@/api/users.js' {
  export const getUsers: (params?: any) => Promise<any>
  export const getUser: (id: any) => Promise<any>
  export const createUser: (data: any) => Promise<any>
  export const updateUser: (id: any, data: any) => Promise<any>
  export const deleteUser: (id: any) => Promise<any>
  export const getUserRoles: (id: any) => Promise<any>
  export const setUserRoles: (id: any, data: any) => Promise<any>
  export const getUserPermissions: (id: any) => Promise<any>
  export const resetUserPassword: (id: any) => Promise<any>
  export const batchDeleteUsers: (data: any) => Promise<any>
  export const batchUpdateUsers: (data: any) => Promise<any>
}

declare module '@/api/roles.js' {
  export const getRoles: (params?: any) => Promise<any>
  export const getRole: (id: any) => Promise<any>
  export const createRole: (data: any) => Promise<any>
  export const updateRole: (id: any, data: any) => Promise<any>
  export const deleteRole: (id: any) => Promise<any>
  export const getRoleMenus: (id: any) => Promise<any>
  export const setRoleMenus: (id: any, data: any) => Promise<any>
  export const getRoleResources: (id: any) => Promise<any>
  export const setRoleResources: (id: any, data: any) => Promise<any>
}

// .js suffix variants

declare module '@/api/firmwares.js' {
  export const getFirmwares: (params?: any) => Promise<any>
  export const getFirmware: (id: any) => Promise<any>
  export const uploadFirmware: (data: any) => Promise<any>
  export const deleteFirmware: (id: any) => Promise<any>
  export const upgradeDevice: (id: any, data: any) => Promise<any>
  export const batchUpgradeDevices: (data: any) => Promise<any>
  export const getFirmwareVersions: (deviceType?: string) => Promise<any>
}

declare module '@/api/files.js' {
  export const getFiles: (params?: any) => Promise<any>
  export const getFile: (id: any) => Promise<any>
  export const uploadFile: (data: any) => Promise<any>
  export const deleteFile: (id: any) => Promise<any>
  export const downloadFile: (id: any, filename?: string) => Promise<any>
  export const getFileUrl: (id: any) => Promise<any>
  export const batchDeleteFiles: (data: any) => Promise<any>
  export const getFileTree: (params?: any) => Promise<any>
}

declare module '@/api/popup-settings.js' {
  export const getPopupSettings: () => Promise<any>
  export const createPopupSetting: (data: any) => Promise<any>
  export const updatePopupSetting: (id: any, data: any) => Promise<any>
  export const deletePopupSetting: (id: any) => Promise<any>
}

declare module '@/api/orgs.js' {
  export const getOrgs: (params?: any) => Promise<any>
  export const getOrg: (id: any) => Promise<any>
  export const createOrg: (data: any) => Promise<any>
  export const updateOrg: (id: any, data: any) => Promise<any>
  export const deleteOrg: (id: any) => Promise<any>
  export const getOrgTree: () => Promise<any>
  export const getOrgUsers: (id: any, params?: any) => Promise<any>
  export const addOrgUsers: (id: any, data: any) => Promise<any>
  export const removeOrgUsers: (id: any, data: any) => Promise<any>
}

declare module '@/api/regions.js' {
  export const getRegions: (params?: any) => Promise<any>
  export const getRegion: (id: any) => Promise<any>
  export const createRegion: (data: any) => Promise<any>
  export const updateRegion: (id: any, data: any) => Promise<any>
  export const deleteRegion: (id: any) => Promise<any>
  export const getRegionTree: () => Promise<any>
  export const getFullRegionTree: () => Promise<any>
  export const getRegionDevices: (id: any, params?: any) => Promise<any>
}

declare module '@/api/video-settings' {
  export const getVideoSettings: (params?: any) => Promise<any>
  export const getVideoSetting: (id: any) => Promise<any>
  export const createVideoSetting: (data: any) => Promise<any>
  export const updateVideoSetting: (id: any, data: any) => Promise<any>
  export const deleteVideoSetting: (id: any) => Promise<any>
  export const toggleVideoSettingStatus: (id: any) => Promise<any>
}

declare module '@/api/video-settings.js' {
  export const getVideoSettings: (params?: any) => Promise<any>
  export const getVideoSetting: (id: any) => Promise<any>
  export const createVideoSetting: (data: any) => Promise<any>
  export const updateVideoSetting: (id: any, data: any) => Promise<any>
  export const deleteVideoSetting: (id: any) => Promise<any>
  export const toggleVideoSettingStatus: (id: any) => Promise<any>
}

declare module '@/api/pt-weight-files' {
  export const getPTWeightFiles: (params?: any) => Promise<any>
  export const getPTWeightFile: (id: any) => Promise<any>
  export const createPTWeightFile: (data: any) => Promise<any>
  export const updatePTWeightFile: (id: any, data: any) => Promise<any>
  export const deletePTWeightFile: (id: any) => Promise<any>
}

declare module '@/api/pt-weight-files.js' {
  export const getPTWeightFiles: (params?: any) => Promise<any>
  export const getPTWeightFile: (id: any) => Promise<any>
  export const createPTWeightFile: (data: any) => Promise<any>
  export const updatePTWeightFile: (id: any, data: any) => Promise<any>
  export const deletePTWeightFile: (id: any) => Promise<any>
}
