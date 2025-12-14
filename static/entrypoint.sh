#!/bin/bash
set -e
python3.12 /app/app.py &
FLASK_PID=$!
for i in {1..30}; do
    if curl -s http://127.0.0.1:5000/ > /dev/null 2>&1; then
        break
    fi
    sleep 1
done
cleanup() {
    kill $FLASK_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGTERM SIGINT
exec httpd -DFOREGROUND
