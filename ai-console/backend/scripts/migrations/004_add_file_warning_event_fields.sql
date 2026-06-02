-- Migration: add warning_event_id and source_type to file table
-- Created: 2026-06-02

-- Add warning_event_id foreign key
ALTER TABLE file
    ADD COLUMN warning_event_id BIGINT,
    ADD COLUMN source_type VARCHAR(30),
    ADD CONSTRAINT fk_file_warning_event
        FOREIGN KEY (warning_event_id) REFERENCES warning_event(id) ON DELETE CASCADE;

-- Add CHECK constraint to restrict source_type values
ALTER TABLE file
    ADD CONSTRAINT chk_file_source_type
        CHECK (source_type IS NULL OR source_type IN ('warning_event_image', 'warning_event_video'));

-- Add indexes
CREATE INDEX idx_file_warning_event ON file(warning_event_id);
CREATE INDEX idx_file_source_type ON file(source_type);
CREATE INDEX idx_file_warning_source ON file(warning_event_id, source_type);
CREATE UNIQUE INDEX idx_file_warning_event_source_unique ON file(warning_event_id, source_type) WHERE deleted_at IS NULL;
