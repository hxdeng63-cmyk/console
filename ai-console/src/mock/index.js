// super-admin
export { menuList } from './super-admin/menu.js'
export { resourceList } from './super-admin/resource.js'
export { microserviceList } from './super-admin/microservice.js'
export { uiCustomizeList } from './super-admin/uiCustomize.js'
export { licenseList } from './super-admin/license.js'

// user-center
export { userList } from './user-center/users.js'
export { organizationList } from './user-center/organizations.js'
export { roleList } from './user-center/roles.js'
export { operationList } from './user-center/operations.js'

// device
export { dataSourceList } from './device/dataSources.js'
export { deviceGroupList } from './device/deviceGroups.js'
export { regionList } from './device/regions.js'
export { platformList } from './device/access/platforms.js'
export { gb28181List } from './device/access/gb28181.js'
export { onvifList } from './device/access/onvif.js'

// linkage
export { taskList } from './linkage/tasks.js'
export { ruleList } from './linkage/rules.js'
export { pushHistoryList } from './linkage/pushHistory.js'

// system
export { videoSettingList } from './system/videoSettings.js'
export { fileList } from './system/files.js'
export { popupSetting } from './system/popupSettings.js'
export { disposeTagList } from './system/disposeTags.js'

// dataClean
export { cleanRecordList } from './dataClean/cleanRecords.js'

// algorithm
export { algorithmList } from './algorithm/algorithms.js'
export { eventList } from './algorithm/events.js'
export { serviceList } from './algorithm/services.js'

// firmware
export { firmwareList } from './firmware/firmware.js'

// events
export { warningEventList } from './events/warningEvents.js'

// event-stats
export * from './event-stats/data'

// event-manage (no mock data needed - Events.vue uses inline static data)

// deployment
export * from './deployment/data'

// monitor
export * from './monitor/data'
export * from './monitor/fileAnalysis'
