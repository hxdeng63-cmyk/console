export interface AlarmItem {
  id: number | string
  time: string
  type: string
  device?: string
  deviceName?: string
  location?: string
  eventDetail?: string
  level?: 'info' | 'warning' | 'danger'
  handled?: boolean
  processStatus?: string
  isCompliant?: boolean | null
  imageUrl?: string
  videoUrl?: string
  captureTime?: string
}