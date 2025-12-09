# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create storage directories
RUN mkdir -p storage/files storage/meeting_logs

# Expose port
EXPOSE 5001
FROM jenkins/jenkins:lts

USER root

# Install Git with OpenSSL support
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    libcurl4-openssl-dev \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

USER jenkins
# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "app.py"]
