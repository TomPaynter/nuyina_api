FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    pynmea2 \
    psycopg2-binary

# COPY ingest.py .

CMD ["python", "/ingest.py"]
