export const ROAD_LEVEL_TEXT_MAP: Record<number, string> = {
  1: '畅通',
  2: '基本畅通',
  3: '缓慢',
  4: '拥堵',
  5: '严重拥堵',
}

/** 由 traffic-api jam 检测结果推断道路等级 1-5 */
export function roadLevelFromJam(isJam: boolean, confidence: number): number {
  if (isJam) return 4
  if (confidence > 0.5) return 3
  return 1
}

export function roadLevelText(level: number): string {
  return ROAD_LEVEL_TEXT_MAP[level] || '畅通'
}