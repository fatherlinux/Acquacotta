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
