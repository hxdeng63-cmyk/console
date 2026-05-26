-- ============================================================
-- Flyway Callback: beforeMigrate
-- 每次迁移执行前触发（包括 validate 后、实际 migrate 前）
-- 文件名必须是 beforeMigrate.sql，放在 callbacks 目录
-- ============================================================

-- 检查数据库编码
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_database
        WHERE datname = current_database()
        AND pg_encoding_to_char(encoding) = 'UTF8'
    ) THEN
        RAISE EXCEPTION '数据库编码必须是 UTF-8';
    END IF;
END $$;

-- 检查 PostgreSQL 版本
DO $$
BEGIN
    IF current_setting('server_version_num')::int < 140000 THEN
        RAISE WARNING '建议 PostgreSQL 14+，当前版本: %', current_setting('server_version');
    END IF;
END $$;
