# Use Python 3.11 as base image
FROM python:3.11-slim

# Install curl
RUN apt-get update && apt-get install -y curl

# Set working directory
WORKDIR /app

# Copy requirements file
COPY app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and bin directory
COPY app/ .
COPY bin/ ./bin/

# Make the message script executable
RUN chmod +x ./bin/message

# Verify ffmpeg installation
RUN ffmpeg -version && python -c "import ffmpeg; print('ffmpeg-python package is installed')"

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "chat.py"]