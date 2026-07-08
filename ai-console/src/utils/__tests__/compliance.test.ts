import { describe, it, expect } from 'vitest'
import { formatCompliance } from '../compliance'

describe('formatCompliance', () => {
  it('boolean true → 合规', () => {
    expect(formatCompliance(true)).toBe('合规')
  })

  it('boolean false → 不合规', () => {
    expect(formatCompliance(false)).toBe('不合规')
  })

  it("string '是' → 合规", () => {
    expect(formatCompliance('是')).toBe('合规')
  })

  it("string '否' → 不合规", () => {
    expect(formatCompliance('否')).toBe('不合规')
  })

  it('null/undefined → 未知', () => {
    expect(formatCompliance(null)).toBe('未知')
    expect(formatCompliance(undefined)).toBe('未知')
  })

  it('其它字符串 → 未知', () => {
    expect(formatCompliance('未知')).toBe('未知')
    expect(formatCompliance('')).toBe('未知')
    expect(formatCompliance('maybe')).toBe('未知')
  })
})
