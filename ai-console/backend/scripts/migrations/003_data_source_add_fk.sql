-- Migration: DataSource 添加外键关联
-- 加 device_id, region_id, org_id 列

ALTER TABLE data_source ADD COLUMN IF NOT EXISTS device_id INTEGER REFERENCES device(id);
ALTER TABLE data_source ADD COLUMN IF NOT EXISTS region_id INTEGER REFERENCES region(id);
ALTER TABLE data_source ADD COLUMN IF NOT EXISTS org_id INTEGER REFERENCES organization(id);

CREATE INDEX IF NOT EXISTS idx_data_source_device ON data_source(device_id);
CREATE INDEX IF NOT EXISTS idx_data_source_region ON data_source(region_id);
CREATE INDEX IF NOT EXISTS idx_data_source_org ON data_source(org_id);
