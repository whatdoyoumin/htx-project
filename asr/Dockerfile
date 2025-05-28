# asr/Dockerfile

# Use a Python base image that also includes package management for ffmpeg
FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install ffmpeg and other necessary system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    libavcodec-dev \
    libavformat-dev \
    libswresample-dev \
    && rm -rf /var/lib/apt/lists/* # Clean up apt caches to reduce image size

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

# Copy the application code into the container
COPY asr/asr_api.py .

# Expose the port on which the FastAPI application will run
EXPOSE 8001

# Command to run the application using Uvicorn
CMD ["uvicorn", "asr_api:app", "--host", "0.0.0.0", "--port", "8001"]