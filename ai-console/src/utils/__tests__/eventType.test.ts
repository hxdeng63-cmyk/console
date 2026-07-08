import { describe, it, expect } from 'vitest'
import { getEventTypeDisplayName } from '../eventType'

describe('getEventTypeDisplayName', () => {
  it('jam → 交通阻塞', () => {
    expect(getEventTypeDisplayName('jam')).toBe('交通阻塞')
  })
  it('flow → 车流量', () => {
    expect(getEventTypeDisplayName('flow')).toBe('车流量')
  })
  it('未知类型返回原值', () => {
    expect(getEventTypeDisplayName('unknown_type')).toBe('unknown_type')
  })
})
