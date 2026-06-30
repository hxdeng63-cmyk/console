-- Rollback: remove device_id column and partial unique index from deployment table
DROP INDEX IF EXISTS idx_deployment_device_module_active;
ALTER TABLE deployment DROP COLUMN IF EXISTS device_id;
