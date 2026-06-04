-- Rollback: remove schedule column from deployment table
ALTER TABLE deployment DROP COLUMN IF EXISTS schedule;
