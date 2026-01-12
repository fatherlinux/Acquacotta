#!/bin/bash
set -e

# Auto-generate self-signed SSL certificates if not bind-mounted
CERT_FILE="/etc/pki/tls/certs/origin.crt"
KEY_FILE="/etc/pki/tls/private/origin.key"

if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
    echo "SSL certificates not found, generating self-signed certificates..."
    mkdir -p /etc/pki/tls/certs /etc/pki/tls/private
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$KEY_FILE" \
        -out "$CERT_FILE" \
        -subj "/CN=localhost/O=Acquacotta/C=US" \
        2>/dev/null
    chmod 600 "$KEY_FILE"
    echo "Self-signed SSL certificates generated."
fi

# Start Flask with Gunicorn (production WSGI server)
start_flask() {
    gunicorn --bind 127.0.0.1:5000 --workers 2 --access-logfile - --error-logfile - app:app &
    FLASK_PID=$!
    echo "Gunicorn started with PID $FLASK_PID"
}

# Wait for Flask to be ready
wait_for_flask() {
    for i in {1..30}; do
        if curl -s http://127.0.0.1:5000/ > /dev/null 2>&1; then
            echo "Flask is ready"
            return 0
        fi
        sleep 1
    done
    echo "Flask failed to start within 30 seconds"
    return 1
}

# Flask supervisor loop - restarts Flask if it exits
supervise_flask() {
    while true; do
        if ! kill -0 $FLASK_PID 2>/dev/null; then
            echo "Flask (PID $FLASK_PID) exited, restarting..."
            start_flask
            sleep 2  # Brief delay before checking readiness
        fi
        sleep 5  # Check every 5 seconds
    done
}

start_flask
wait_for_flask

# Start Flask supervisor in background
supervise_flask &
SUPERVISOR_PID=$!

cleanup() {
    kill $SUPERVISOR_PID 2>/dev/null || true
    kill $FLASK_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGTERM SIGINT
exec httpd -DFOREGROUND
