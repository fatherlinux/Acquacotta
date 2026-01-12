FROM registry.access.redhat.com/ubi10/ubi:latest

RUN dnf install -y python3.12 python3.12-pip httpd mod_ssl openssl procps-ng && dnf clean all

WORKDIR /app

COPY requirements.txt .
RUN pip3.12 install --no-cache-dir -r requirements.txt

COPY app.py .
COPY sheets_storage.py .
COPY templates/ templates/
COPY static/ static/

# Apache SSL reverse proxy configuration
COPY static/acquacotta-ssl.conf /etc/httpd/conf.d/acquacotta-ssl.conf
RUN rm -f /etc/httpd/conf.d/ssl.conf

# Entrypoint script
COPY static/entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh

ENV FLASK_HOST=127.0.0.1

EXPOSE 443

CMD ["/entrypoint.sh"]
