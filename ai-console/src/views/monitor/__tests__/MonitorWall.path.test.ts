import { describe, it, expect } from 'vitest'

// 提取路径拼接逻辑(原本在 MonitorWall.vue:198)
function buildChannelName(path: string[], deviceName: string): string {
  const prefix = path.join('-').replaceAll('-', ' ')
  return `${prefix}-${deviceName}`
}

describe('buildChannelName', () => {
  it('替换所有 - 为空格', () => {
    expect(buildChannelName(['海东公司', '大学城北', '北区'], '设备1'))
      .toBe('海东公司 大学城北 北区-设备1')
  })

  it('单层路径', () => {
    expect(buildChannelName(['公司A'], '设备1')).toBe('公司A-设备1')
  })

  it('空路径', () => {
    expect(buildChannelName([], '设备1')).toBe('-设备1')
  })

  it('对比 bug 版本(只替第一个)', () => {
    // 验证旧实现是错的
    const buggy = ['海东公司', '大学城北', '北区'].join('-').replace('-', ' ')
    expect(buggy).toBe('海东公司 大学城北-北区')  // bug: 第二个 - 没替
    const fixed = ['海东公司', '大学城北', '北区'].join('-').replaceAll('-', ' ')
    expect(fixed).toBe('海东公司 大学城北 北区')  // 正确
    expect(fixed).not.toBe(buggy)
  })
})
