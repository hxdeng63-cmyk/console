-- Add device_id column to deployment table for denormalized unique constraint
ALTER TABLE deployment ADD COLUMN IF NOT EXISTS device_id INTEGER NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_deployment_device_module_active
ON deployment (device_id, module_name)
WHERE deleted_at IS NULL;
