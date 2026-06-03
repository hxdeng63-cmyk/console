-- 事件统计索引优化
-- 为 warning_event 表添加复合索引和函数索引，支撑实时聚合查询

-- 支撑按 event_type 分组的统计（今日、不合规、场景）
CREATE INDEX IF NOT EXISTS idx_warning_stats_event_type
ON warning_event(org_id, region_id, event_type_id, report_time)
WHERE deleted_at IS NULL;

-- 支撑按 algorithm 分组的统计
CREATE INDEX IF NOT EXISTS idx_warning_stats_algo
ON warning_event(org_id, region_id, algorithm_id, report_time)
WHERE deleted_at IS NULL;

-- 支撑趋势统计（按时间分组）
CREATE INDEX IF NOT EXISTS idx_warning_stats_trend
ON warning_event(org_id, region_id, report_time, algorithm_id, event_type_id)
WHERE deleted_at IS NULL;

-- 函数索引：支撑 COALESCE(report_time, created_at) 的范围过滤
CREATE INDEX IF NOT EXISTS idx_warning_stats_report_time_coalesce
ON warning_event(COALESCE(report_time, created_at))
WHERE deleted_at IS NULL;
