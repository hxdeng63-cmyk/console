/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module '@/stores/tabs' {
  const useTabsStore: any
  export { useTabsStore }
}

declare module '@/mock' {
  export const menuList: any
  export const resourceList: any
  export const microserviceList: any
  export const uiCustomizeList: any
  export const licenseList: any
  export const userList: any
  export const organizationList: any
  export const roleList: any
  export const operationList: any
  export const dataSourceList: any
  export const syncDeviceList: any
  export const deviceList: any
  export const deviceGroupList: any
  export const regionList: any
  export const platformList: any
  export const gb28181List: any
  export const onvifList: any
  export const taskList: any
  export const ruleList: any
  export const pushHistoryList: any
  export const videoSettingList: any
  export const fileList: any
  export const popupSetting: any
  export const disposeTagList: any
  export const cleanRecordList: any
  export const algorithmList: any
  export const eventList: any
  export const serviceList: any
  export const firmwareList: any
  export const warningEventList: any
}
