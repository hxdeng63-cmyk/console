import { describe, it, expect } from 'vitest'
import { parseDateTime, formatDateTime } from '../date'

describe('parseDateTime', () => {
  it('null/undefined/空串 → null', () => {
    expect(parseDateTime(null)).toBeNull()
    expect(parseDateTime(undefined)).toBeNull()
    expect(parseDateTime('')).toBeNull()
  })

  it('Date 实例直接返回 (有效)', () => {
    const d = new Date('2026-07-01T12:00:00Z')
    expect(parseDateTime(d)).toBe(d)
  })

  it('Date 实例无效 → null', () => {
    const d = new Date('')
    expect(parseDateTime(d)).toBeNull()
  })

  it('naive ISO 补 +08:00', () => {
    // 业务时区 12:00 → UTC 04:00
    expect(parseDateTime('2026-07-01T12:00:00')?.toISOString()).toBe('2026-07-01T04:00:00.000Z')
  })

  it('带 TZ 的 ISO 原样解析', () => {
    expect(parseDateTime('2026-07-01T12:00:00+08:00')?.toISOString()).toBe('2026-07-01T04:00:00.000Z')
  })

  it('带 Z 的 ISO 解析', () => {
    expect(parseDateTime('2026-07-01T12:00:00Z')?.toISOString()).toBe('2026-07-01T12:00:00.000Z')
  })

  it('无法解析 → null', () => {
    expect(parseDateTime('not a date')).toBeNull()
  })
})

describe('formatDateTime', () => {
  it('空值 → 空串', () => {
    expect(formatDateTime(null)).toBe('')
    expect(formatDateTime(undefined)).toBe('')
    expect(formatDateTime('')).toBe('')
  })

  it('格式化为 YYYY年MM月DD日 HH点mm分ss秒', () => {
    // 用 naive 形式 (业务 TZ +08:00)
    const out = formatDateTime('2026-07-01T12:34:56')
    expect(out).toBe('2026年07月01日 12点34分56秒')
  })

  it('解析失败 → 空串', () => {
    expect(formatDateTime('garbage')).toBe('')
  })

  it('Date 实例可格式化', () => {
    const d = new Date('2026-01-05T03:04:05Z')
    const out = formatDateTime(d)
    expect(out).toMatch(/^\d{4}年\d{2}月\d{2}日 \d{2}点\d{2}分\d{2}秒$/)
  })
})
