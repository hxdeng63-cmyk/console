-- Migration: Add new fields to linkage_rule for notification channels

BEGIN;

-- Add delay/scheduled fields
ALTER TABLE linkage_rule
    ADD COLUMN IF NOT EXISTS delay_value INTEGER,
    ADD COLUMN IF NOT EXISTS delay_unit VARCHAR(20),
    ADD COLUMN IF NOT EXISTS scheduled_time TIMESTAMP;

-- Add WeChat-specific fields
ALTER TABLE linkage_rule
    ADD COLUMN IF NOT EXISTS wechat_app_id VARCHAR(100),
    ADD COLUMN IF NOT EXISTS wechat_app_secret VARCHAR(255),
    ADD COLUMN IF NOT EXISTS wechat_template_id VARCHAR(100);

-- Add SMS field
ALTER TABLE linkage_rule
    ADD COLUMN IF NOT EXISTS sms_id VARCHAR(100);

COMMIT;
