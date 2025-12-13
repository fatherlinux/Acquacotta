#!/bin/bash
# Acquacotta launcher - starts Flask server and opens browser

export FLASK_APP=/app/bin/acquacotta-server
export TEMPLATES_DIR=/app/share/acquacotta/templates

cd /app/share/acquacotta

# Start the server in background
python3 /app/bin/acquacotta-server &
SERVER_PID=$!

# Wait for server to start
sleep 2

# Open browser
xdg-open http://localhost:5000 2>/dev/null || echo "Open http://localhost:5000 in your browser"

# Wait for server
wait $SERVER_PID
