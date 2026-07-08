import { describe, it, expect } from 'vitest'
import { detectFileType } from '../fileType'

describe('detectFileType', () => {
  it('图片扩展名 → 图片', () => {
    expect(detectFileType('a.jpg')).toBe('图片')
    expect(detectFileType('a.jpeg')).toBe('图片')
    expect(detectFileType('a.png')).toBe('图片')
    expect(detectFileType('a.gif')).toBe('图片')
    expect(detectFileType('a.bmp')).toBe('图片')
    expect(detectFileType('a.webp')).toBe('图片')
  })

  it('视频扩展名 → 视频', () => {
    expect(detectFileType('a.mp4')).toBe('视频')
    expect(detectFileType('a.webm')).toBe('视频')
    expect(detectFileType('a.ogg')).toBe('视频')
    expect(detectFileType('a.mov')).toBe('视频')
  })

  it('未知扩展名 → fallback (默认图片)', () => {
    expect(detectFileType('a.txt')).toBe('图片')
  })

  it('未知扩展名 → 自定义 fallback', () => {
    expect(detectFileType('a.txt', '视频')).toBe('视频')
  })

  it('无扩展名 → fallback', () => {
    expect(detectFileType('noext')).toBe('图片')
  })

  it('大小写不敏感', () => {
    expect(detectFileType('a.JPG')).toBe('图片')
    expect(detectFileType('a.MP4')).toBe('视频')
  })
})
