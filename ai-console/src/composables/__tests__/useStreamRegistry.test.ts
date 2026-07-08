import { describe, it, expect } from 'vitest'
import { setStreamMapEntry } from '../useStreamRegistry'

describe('setStreamMapEntry', () => {
  it('writes entry with url + sourceType', () => {
    const result = setStreamMapEntry({}, 42, { url: 'http://x/flv', sourceType: 'stream' })
    expect(result['device-42']).toEqual({
      url: 'http://x/flv',
      sourceType: 'stream',
      deviceFallbackUrl: null,
    })
  })

  it('preserves other entries', () => {
    const prev = {
      'device-1': { url: 'a', sourceType: 'stream', deviceFallbackUrl: '/a.mp4' },
    }
    const result = setStreamMapEntry(prev, 2, { url: 'b', sourceType: 'stream', deviceFallbackUrl: '/b.mp4' })
    expect(result['device-1']).toEqual({ url: 'a', sourceType: 'stream', deviceFallbackUrl: '/a.mp4' })
    expect(result['device-2']).toEqual({ url: 'b', sourceType: 'stream', deviceFallbackUrl: '/b.mp4' })
  })

  it('overwrites same device-id', () => {
    const prev = { 'device-1': { url: 'old', sourceType: 'stream', deviceFallbackUrl: '/old.mp4' } }
    const result = setStreamMapEntry(prev, 1, { url: 'new', sourceType: 'local', deviceFallbackUrl: '/new.mp4' })
    expect(result['device-1'].url).toBe('new')
    expect(result['device-1'].sourceType).toBe('local')
    expect(result['device-1'].deviceFallbackUrl).toBe('/new.mp4')
  })

  it('normalizes undefined deviceFallbackUrl to null', () => {
    const result = setStreamMapEntry({}, 1, { url: 'a', sourceType: 'stream' })
    expect(result['device-1'].deviceFallbackUrl).toBeNull()
  })

  it('preserves null deviceFallbackUrl explicitly', () => {
    const result = setStreamMapEntry({}, 1, { url: 'a', sourceType: 'stream', deviceFallbackUrl: null })
    expect(result['device-1'].deviceFallbackUrl).toBeNull()
  })

  it('preserves non-null deviceFallbackUrl', () => {
    const result = setStreamMapEntry({}, 1, { url: 'a', sourceType: 'stream', deviceFallbackUrl: '/x.mp4' })
    expect(result['device-1'].deviceFallbackUrl).toBe('/x.mp4')
  })

  it('accepts string deviceId', () => {
    const result = setStreamMapEntry({}, '99', { url: 'a', sourceType: 'stream' })
    expect(result['device-99']).toBeDefined()
  })
})
