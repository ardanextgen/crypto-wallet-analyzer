# Python 3.11 Base Image
FROM python:3.11-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# System-Dependencies installieren
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Requirements kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Gesamten Code kopieren
COPY . .

# Port exposieren (Railway setzt $PORT automatisch)
EXPOSE 8000

# Start-Kommando (Railway setzt $PORT automatisch)
CMD ["sh", "-c", "uvicorn src.api.server:app --host 0.0.0.0 --port $PORT"]
