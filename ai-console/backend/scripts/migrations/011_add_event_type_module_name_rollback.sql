-- Rollback: remove module_name column from event_type table
DROP INDEX IF EXISTS idx_event_type_module_name;
ALTER TABLE event_type DROP COLUMN IF EXISTS module_name;
