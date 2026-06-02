-- Incremental fix: add missing source_type, constraints, indexes
-- Created: 2026-06-02

-- 1. Add source_type if missing
ALTER TABLE file ADD COLUMN IF NOT EXISTS source_type VARCHAR(30);

-- 2. Recreate FK with ON DELETE CASCADE (drop auto-named old one first)
ALTER TABLE file DROP CONSTRAINT IF EXISTS file_warning_event_id_fkey;
ALTER TABLE file DROP CONSTRAINT IF EXISTS fk_file_warning_event;
ALTER TABLE file ADD CONSTRAINT fk_file_warning_event
    FOREIGN KEY (warning_event_id) REFERENCES warning_event(id) ON DELETE CASCADE;

-- 3. Add CHECK constraint
ALTER TABLE file DROP CONSTRAINT IF EXISTS chk_file_source_type;
ALTER TABLE file ADD CONSTRAINT chk_file_source_type
    CHECK (source_type IS NULL OR source_type IN ('warning_event_image', 'warning_event_video'));

-- 4. Add indexes (idempotent: drop then create to avoid conflicts)
DROP INDEX IF EXISTS idx_file_warning_event;
DROP INDEX IF EXISTS idx_file_source_type;
DROP INDEX IF EXISTS idx_file_warning_source;
DROP INDEX IF EXISTS idx_file_warning_event_source_unique;

CREATE INDEX idx_file_warning_event ON file(warning_event_id);
CREATE INDEX idx_file_source_type ON file(source_type);
CREATE INDEX idx_file_warning_source ON file(warning_event_id, source_type);
CREATE UNIQUE INDEX idx_file_warning_event_source_unique ON file(warning_event_id, source_type) WHERE deleted_at IS NULL;
