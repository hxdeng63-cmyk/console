-- Rollback: shrink deployment_token back to VARCHAR(64).
-- WARNING: any rows with deployment_token longer than 64 chars will fail this migration.
ALTER TABLE deployment
    ALTER COLUMN deployment_token TYPE VARCHAR(64);