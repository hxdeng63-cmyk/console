-- Widen deployment_token from VARCHAR(64) to VARCHAR(255)
-- Reason: traffic-api callback tokens may exceed 64 chars (prefixes, random segments),
--          risking silent truncation or DB error.
-- Safe for existing data: VARCHAR(64) values remain valid in VARCHAR(255).
ALTER TABLE deployment
    ALTER COLUMN deployment_token TYPE VARCHAR(255);