-- Migration: Add cleanup_policy table and extend clean_record
-- Created: 2026-06-02

-- 1. Create cleanup_policy table
CREATE TABLE IF NOT EXISTS cleanup_policy (
    id BIGSERIAL PRIMARY KEY,
    alert_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    alert_days INTEGER NOT NULL DEFAULT 90,
    video_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    video_days INTEGER NOT NULL DEFAULT 60,
    strategy VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    execute_time VARCHAR(5) DEFAULT '02:00',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by BIGINT,
    updated_by BIGINT,
    deleted_at TIMESTAMPTZ
);

-- 2. Insert default policy record (single global config)
INSERT INTO cleanup_policy (id, alert_enabled, alert_days, video_enabled, video_days, strategy, execute_time)
VALUES (1, TRUE, 90, TRUE, 60, 'scheduled', '02:00')
ON CONFLICT (id) DO NOTHING;

-- 3. Extend clean_record table
ALTER TABLE clean_record
    ADD COLUMN IF NOT EXISTS records_cleaned INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS dimension VARCHAR(20),
    ADD COLUMN IF NOT EXISTS error_message VARCHAR(500);

-- 4. Add index for file cleanup queries (source_type + created_at for video file cleanup)
CREATE INDEX IF NOT EXISTS idx_file_source_created
    ON file (source_type, created_at)
    WHERE deleted_at IS NULL;
