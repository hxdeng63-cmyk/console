ALTER TABLE deployment
    DROP COLUMN IF EXISTS pid,
    DROP COLUMN IF EXISTS config_json,
    DROP COLUMN IF EXISTS started_at,
    DROP COLUMN IF EXISTS stopped_at,
    DROP COLUMN IF EXISTS exit_code,
    DROP COLUMN IF EXISTS log_path,
    DROP COLUMN IF EXISTS module_name,
    DROP COLUMN IF EXISTS deployment_token,
    DROP COLUMN IF EXISTS org_id,
    DROP COLUMN IF EXISTS region_id;
