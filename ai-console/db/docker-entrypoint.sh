#!/bin/bash
# ============================================================
# 数据库启动脚本（替代 postgres 官方 entrypoint）
# 功能：
#   1. 启动 PostgreSQL
#   2. 等待数据库就绪
#   3. 执行所有迁移 SQL 文件（V1, V2, R__）
#   4. 支持重复执行（幂等设计）
# ============================================================

set -e

echo "=== Starting PostgreSQL ==="
# 启动 PostgreSQL（后台运行）
gosu postgres postgres -D /var/lib/postgresql/data &

# 等待 PostgreSQL 就绪
echo "=== Waiting for PostgreSQL to be ready ==="
until gosu postgres pg_isready -q; do
  echo "PostgreSQL not ready, waiting 2s..."
  sleep 2
done
echo "PostgreSQL is ready!"

# 执行迁移脚本
echo "=== Running migrations ==="
for f in /docker-entrypoint-initdb.d/V*.sql /docker-entrypoint-initdb.d/R__*.sql; do
  if [ -f "$f" ]; then
    filename=$(basename "$f")
    echo "Executing $filename ..."
    gosu postgres psql -U postgres -d ai_console -v ON_ERROR_STOP=1 -f "$f"
    echo "Done: $filename"
  fi
done

# 阻止容器退出（保持 postgres 进程运行）
echo "=== Migrations complete. Holding process ==="
wait