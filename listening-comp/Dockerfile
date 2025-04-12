# Base image with Python 3.9
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies including ffmpeg
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies (including ffmpeg-python wrapper)
RUN pip install --no-cache-dir --progress-bar off -r requirements.txt

# Create necessary directories
RUN mkdir -p audio temp

# Copy application code
COPY . .

# Verify ffmpeg installation
RUN ffmpeg -version && python -c "import ffmpeg; print('ffmpeg-python package is installed')"

# Set environment variables
ENV PYTHONPATH=/app

# Expose the port
EXPOSE 8000

# Run the streamlit application
CMD ["streamlit", "run", "frontend/main.py", "--server.port", "8000", "--server.address", "0.0.0.0"]