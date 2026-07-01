export const PROCESS_STATUS_TEXT_MAP: Record<string, string> = {
  pending: '待处理',
  processing: '处理中',
  resolved: '已解决',
  ignored: '已忽略',
}

export const PROCESS_STATUS_TAG_MAP: Record<string, string> = {
  pending: 'warning',
  processing: 'primary',
  resolved: 'success',
  ignored: 'info',
}

export function statusText(status: string): string {
  return PROCESS_STATUS_TEXT_MAP[status] || status
}

export function statusTagType(status: string): string {
  return PROCESS_STATUS_TAG_MAP[status] || ''
}