BEGIN;

ALTER TABLE region ADD COLUMN org_id BIGINT NULL REFERENCES organization(id);
ALTER TABLE region ADD COLUMN remark VARCHAR(500) NULL;
CREATE INDEX idx_region_org ON region(org_id);

COMMIT;
