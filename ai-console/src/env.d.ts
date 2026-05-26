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

declare module '@/api/operation-logs.js' {
  export const getOperationLogs: (params?: Record<string, any>) => Promise<any>
  export const getOperationLog: (id: number | string) => Promise<any>
  export const exportOperationLogs: (params?: Record<string, any>) => Promise<any>
  export const deleteOperationLog: (id: number | string) => Promise<any>
  export const deleteOperationLogs: (data: any) => Promise<any>
}

declare module '@/api/microservices.js' {
  export const getMicroservices: (params?: Record<string, any>) => Promise<any>
  export const getMicroservice: (id: number | string) => Promise<any>
  export const createMicroservice: (data: any) => Promise<any>
  export const updateMicroservice: (id: number | string, data: any) => Promise<any>
  export const deleteMicroservice: (id: number | string) => Promise<any>
}
