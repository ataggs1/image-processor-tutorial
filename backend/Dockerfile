# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py processor.py ./

# Create data directories
RUN mkdir -p /data/uploads /data/processed

# Expose port
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=5000 \
    UPLOAD_FOLDER=/data/uploads \
    PROCESSED_FOLDER=/data/processed

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:create_app()"]
