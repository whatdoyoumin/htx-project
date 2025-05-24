# # Use an official slim Python base
# FROM python:3.11-slim

# # Install ffmpeg at the OS level
# RUN apt-get update \
#     && apt-get install -y --no-install-recommends ffmpeg \
#     && rm -rf /var/lib/apt/lists/*

# # Create app directory and set it as workdir
# WORKDIR /app

# # Copy only your dependency list first (cache this layer when deps don’t change)
# COPY requirements.txt .

# # Install Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy your ASR code into /app/asr
# COPY asr/ ./asr/

# # Switch working directory into the asr folder
# WORKDIR /app/asr

# # Expose the ASR port
# EXPOSE 8001

# # Run the FastAPI/Uvicorn server
# # Note: asr_api.py lives here, so module is just "asr_api"
# CMD ["uvicorn", "asr_api:app", "--host", "0.0.0.0", "--port", "8001"]



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

# Copy the application code into the container
COPY asr/asr_api.py .

# Expose the port on which the FastAPI application will run
EXPOSE 8001

# Command to run the application using Uvicorn
CMD ["uvicorn", "asr_api:app", "--host", "0.0.0.0", "--port", "8001"]