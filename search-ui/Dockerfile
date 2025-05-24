FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Flask and Elasticsearch client
RUN pip install --no-cache-dir flask==3.1.1 elasticsearch==8.13.0


# Copy app code
COPY search_app.py .
COPY templates ./templates

# Expose the port
EXPOSE 3000

# Run the Flask app
CMD ["python", "search_app.py"]
