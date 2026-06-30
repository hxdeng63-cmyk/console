export type FileMediaType = '视频' | '图片'

export function detectFileType(
  name: string,
  fallback: FileMediaType = '图片'
): FileMediaType {
  const ext = name.split('.').pop()?.toLowerCase() || ''
  const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
  const videoExts = ['mp4', 'webm', 'ogg', 'mov']
  if (imageExts.includes(ext)) return '图片'
  if (videoExts.includes(ext)) return '视频'
  return fallback
}
