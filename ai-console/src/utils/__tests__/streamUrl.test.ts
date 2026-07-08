import { describe, it, expect } from 'vitest'
import { isLocalStream, withCacheBuster, pathOnly } from '../streamUrl'

describe('isLocalStream', () => {
  it('rtsp:// 不判定为 local', () => {
    expect(isLocalStream('stream', 'rtsp://x/y')).toBe(false)
  })
  it('.mp4 判定为 local', () => {
    expect(isLocalStream('stream', 'http://x/y.mp4')).toBe(true)
  })
  it('.flv 判定为 stream', () => {
    expect(isLocalStream('stream', 'http://x/y.flv')).toBe(false)
  })
})

describe('withCacheBuster', () => {
  it('添加 _t 查询参数', () => {
    const r = withCacheBuster('http://x/flv', 'stream')
    expect(r).toMatch(/_t=/)
  })
  it('保留原有 query', () => {
    const r = withCacheBuster('http://x/flv?token=abc', 'stream')
    expect(r).toContain('token=abc')
    expect(r).toContain('_t=')
  })
})

describe('pathOnly', () => {
  it('去除 query 和 fragment', () => {
    expect(pathOnly('http://x/y.flv?token=abc#frag')).toBe('http://x/y.flv')
  })
})
