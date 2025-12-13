FROM registry.access.redhat.com/ubi9/python-312:latest

USER 0

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ templates/

RUN chown -R 1001:0 /app && chmod -R g=u /app

USER 1001

EXPOSE 5000

ENV FLASK_HOST=0.0.0.0

CMD ["python", "app.py"]
