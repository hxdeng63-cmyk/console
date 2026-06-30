/**
 * 事件类型中英文映射工具
 *
 * 后端/算法层统一使用英文 code 作为事件类型标识，UI 层通过本工具映射为中文描述。
 * 查询、筛选、表单 value 仍保持英文 code 不变，仅显示文本做中文转换。
 */

export const EVENT_TYPE_NAME_MAP: Record<string, string> = {
  jam: '交通阻塞',
  anomaly: '异常停车',
  flow: '流量统计',
  reverse: '逆向行驶',
  pedestrian: '行人闯入',
  accident: '疑似事故',
  vest: '反光衣检测'
}

export function getEventTypeDisplayName(name: string | undefined | null): string {
  if (!name) return '-'
  return EVENT_TYPE_NAME_MAP[name] || name
}
