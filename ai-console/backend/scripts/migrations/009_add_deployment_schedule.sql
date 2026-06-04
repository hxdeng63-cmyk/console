-- Add schedule column (JSONB) to deployment table
ALTER TABLE deployment ADD COLUMN schedule JSONB NULL;
