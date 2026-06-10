#!/bin/bash
# Start mediamtx media server
# Usage: ./start-mediamtx.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -f "./mediamtx" ]; then
    echo "Error: mediamtx binary not found in $SCRIPT_DIR"
    echo "Download from: https://github.com/bluenviron/mediamtx/releases"
    exit 1
fi

echo "Starting mediamtx..."
echo "  RTSP:  :8554"
echo "  HTTP:  :8888 (HTTP-FLV)"
echo "  API:   :9997"
./mediamtx mediamtx.yml
