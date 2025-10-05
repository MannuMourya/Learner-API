# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends     build-essential curl libpq-dev &&     rm -rf /var/lib/apt/lists/*

# Copy and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY app ./app

# Data dir for uploads
RUN mkdir -p /data
# VOLUME ["/data"]

ENV HOST=0.0.0.0 PORT=8000 WORKERS=2 LOG_LEVEL=info

EXPOSE 8000

# Gunicorn w/ uvicorn workers
CMD ["sh", "-c", "python -m app.db.init_db && gunicorn -w ${WORKERS} -k uvicorn.workers.UvicornWorker -b ${HOST}:${PORT} app.main:app --log-level ${LOG_LEVEL}"]
