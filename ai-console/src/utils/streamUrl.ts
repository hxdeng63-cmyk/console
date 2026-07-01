const DIRECT_VIDEO_EXT = /\.(mp4|webm|ogg|mov)(\?.*)?$/i

export function isDirectVideoUrl(url: string): boolean {
  if (!url) return false
  // strip query string before testing extension
  return DIRECT_VIDEO_EXT.test(url.toLowerCase().split('?')[0])
}

export function isLocalStream(sourceType: string, url: string): boolean {
  return sourceType === 'local' || isDirectVideoUrl(url)
}

export function withCacheBuster(url: string, sourceType: string): string {
  if (sourceType !== 'local') return url
  if (!url) return url
  const separator = url.includes('?') ? '&' : '?'
  return `${url}${separator}_t=${Date.now()}`
}

/** 仅取路径（去 query），用于协议判断 */
export function pathOnly(url: string): string {
  return (url || '').split('?')[0]
}