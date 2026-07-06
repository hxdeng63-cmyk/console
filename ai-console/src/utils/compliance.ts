/**
 * 合规状态格式化工具
 *
 * 后端 algorithm-events 与 warning-events 对同一字段返回不同类型：
 * - warning-events: boolean (true / false / null)
 * - algorithm-events: string ('是' / '否' / '未知')
 * 早期 Events.vue 直接渲染字符串导致与 Monitor 系列 3 态 ternary 不一致。
 *
 * 本工具同时接受 boolean 与 string 输入，统一返回 '合规' / '不合规' / '未知'，
 * 所有视图共享同一渲染结果。
 */

export function formatCompliance(value: boolean | string | null | undefined): string {
  if (value === true || value === '是') return '合规'
  if (value === false || value === '否') return '不合规'
  return '未知'
}