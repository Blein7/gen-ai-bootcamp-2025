# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set permissions for the application directory
RUN rm -f words.db && \
    rm -rf instance && \
    chmod -R 755 /app && \
    chmod 777 /app

# Set environment variables
ENV FLASK_APP=app.py

# Make the entrypoint script executable
RUN chmod +x /app/docker/entrypoint.sh

# Use entrypoint script
CMD ["/bin/bash", "/app/docker/entrypoint.sh"]