FROM python:3.11-slim

WORKDIR /app

# Install only what's needed
RUN pip install --no-cache-dir pandas requests

COPY cv-index.py .

CMD ["python", "cv-index.py"]
