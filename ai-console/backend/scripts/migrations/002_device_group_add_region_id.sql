-- Migration: DeviceGroup 改造
-- 去掉 parent_id（自引用树），加 region_id（关联区域）

ALTER TABLE device_group DROP COLUMN IF EXISTS parent_id;
ALTER TABLE device_group ADD COLUMN IF NOT EXISTS region_id INTEGER REFERENCES region(id);
CREATE INDEX IF NOT EXISTS idx_device_group_region ON device_group(region_id);
