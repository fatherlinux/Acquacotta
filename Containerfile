# Production image for Acquacotta
# Built on top of acquacotta-base - only contains app code
# Very fast to build since infrastructure is pre-cached
#
# Build: podman build -t quay.io/fatherlinux/acquacotta .

FROM quay.io/fatherlinux/acquacotta-base:latest

WORKDIR /app

# Copy only application code (fast)
COPY app.py .
COPY sheets_storage.py .
COPY templates/ templates/
COPY static/ static/

CMD ["/entrypoint.sh"]
