# Root Dockerfile that sets build context to backend/
# This is needed because Railway builds from repo root
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-nor \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from backend directory
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code from backend directory
COPY backend/ .

# Create uploads directory
RUN mkdir -p uploads

# Expose port (Railway uses PORT env var)
EXPOSE 8000

# Run application (Railway will override with PORT env var via railway.json)
# Use shell form to allow env var expansion
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
