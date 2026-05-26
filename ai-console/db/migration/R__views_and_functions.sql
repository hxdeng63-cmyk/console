-- ============================================================
-- Flyway Repeatable Migration: R__views_and_functions
-- 可重复执行：每次 checksum 变化时 Flyway 会自动重新执行
-- 适用场景：视图、函数、存储过程（可安全 drop + create）
-- ============================================================

-- --------------------------------------------------------------
-- 1. 视图
-- --------------------------------------------------------------

-- 设备完整信息视图（含区域、组织、主码流）
CREATE OR REPLACE VIEW v_device_full AS
SELECT
    d.id,
    d.device_code,
    d.name AS device_name,
    d.status,
    d.access_type,
    d.device_type,
    d.longitude,
    d.latitude,
    r.name AS region_name,
    o.name AS org_name,
    ds.stream_url AS primary_stream_url,
    ds.resolution,
    ds.fps
FROM device d
LEFT JOIN region r ON r.id = d.region_id AND r.deleted_at IS NULL
LEFT JOIN organization o ON o.id = d.org_id AND o.deleted_at IS NULL
LEFT JOIN device_stream ds ON ds.device_id = d.id AND ds.is_primary = true AND ds.deleted_at IS NULL
WHERE d.deleted_at IS NULL;

COMMENT ON VIEW v_device_full IS '设备完整信息视图，含区域、组织和主码流';

-- 用户权限视图
CREATE OR REPLACE VIEW v_user_roles AS
SELECT
    u.id AS user_id,
    u.username,
    u.real_name,
    r.id AS role_id,
    r.name AS role_name,
    r.code AS role_code
FROM "user" u
JOIN user_role ur ON ur.user_id = u.id
JOIN role r ON r.id = ur.role_id
WHERE u.deleted_at IS NULL AND r.deleted_at IS NULL;

COMMENT ON VIEW v_user_roles IS '用户-角色关联视图';

-- --------------------------------------------------------------
-- 2. 函数
-- --------------------------------------------------------------

-- 通用更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 预警事件归档函数
CREATE OR REPLACE FUNCTION archive_old_warning_events(cutoff_date DATE)
RETURNS INT AS $$
DECLARE
    archived_count INT;
BEGIN
    INSERT INTO warning_event_archive
    SELECT *, NOW() FROM warning_event
    WHERE report_time < cutoff_date;

    GET DIAGNOSTICS archived_count = ROW_COUNT;

    DELETE FROM warning_event WHERE report_time < cutoff_date;

    RETURN archived_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION archive_old_warning_events IS '将指定日期之前的预警事件归档到历史表';
