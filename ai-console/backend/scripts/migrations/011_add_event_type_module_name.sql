-- Add module_name column to event_type table
ALTER TABLE event_type ADD COLUMN IF NOT EXISTS module_name VARCHAR(50) NULL;

CREATE INDEX IF NOT EXISTS idx_event_type_module_name ON event_type(module_name);
