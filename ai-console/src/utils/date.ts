/**
 * 日期时间格式化工具
 *
 * 后端 WarningEvent.report_time (DateTime(timezone=True)) 经 .isoformat() 序列化后，
 * 可能是带时区的 aware ISO ("2026-07-01T20:57:18+08:00")，
 * 也可能是 fallback 到 created_at 的 naive ISO ("2026-07-01T20:57:18", 无时区后缀)。
 *
 * 本工具对两种形态做容错解析：naive 一律按业务时区 Asia/Shanghai (+08:00) 解读，
 * 避免浏览器本地时区差异造成展示偏移。展示格式固定为
 * 「YYYY年MM月DD日 HH点mm分ss秒」，与用户运营场景对齐。
 */

/** 业务时区偏移量 (Asia/Shanghai)；项目内 implicit TZ，未来调整只改此处 */
const BUSINESS_TZ_OFFSET = '+08:00'

/** 匹配 naive ISO：YYYY-MM-DD[T| ]HH:mm:ss，无时区/毫秒后缀 */
const NAIVE_ISO = /^(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})$/

/** 是否已带时区设计符：Z 或 ±HH:MM 结尾 */
const HAS_TZ = /Z$|[+-]\d{2}:\d{2}$/

/**
 * 把任意输入归一化到 ISO 8601 with offset，确保 JS Date 解析稳定。
 * - 已带 TZ：原样
 * - naive ISO：补 +08:00
 * - 其它：原样（让 Date 自行尝试解析，失败则返回 null）
 */
function normalize(input: string): string {
  if (HAS_TZ.test(input)) return input
  const m = input.match(NAIVE_ISO)
  if (m) return `${m[1]}T${m[2]}${BUSINESS_TZ_OFFSET}`
  return input
}

/**
 * 容错解析日期时间。
 * - null/undefined/空字符串 → null
 * - Date 实例 → 直接返回（无效 Date 走 NaN 检查返回 null）
 * - string：naive 补 +08:00 后解析；解析失败返回 null
 */
export function parseDateTime(input: string | Date | null | undefined): Date | null {
  if (input == null) return null
  if (input instanceof Date) {
    return isNaN(input.getTime()) ? null : input
  }
  const s = String(input).trim()
  if (!s) return null
  const d = new Date(normalize(s))
  return isNaN(d.getTime()) ? null : d
}

/**
 * 把任意日期输入格式化为「YYYY年MM月DD日 HH点mm分ss秒」。
 * 时分秒 0 填充；解析失败或空值返回 ''。
 */
export function formatDateTime(input: string | Date | null | undefined): string {
  const d = parseDateTime(input)
  if (!d) return ''
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}年${pad(d.getMonth() + 1)}月${pad(d.getDate())}日 ${pad(d.getHours())}点${pad(d.getMinutes())}分${pad(d.getSeconds())}秒`
}