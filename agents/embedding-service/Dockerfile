FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY service.py .

# Copy shared modules from parent directory
COPY ../embedding_service.py .
COPY ../cache_manager.py .
COPY ../ai_config.py .

# Expose port
EXPOSE 8006

# Run service
CMD ["python", "service.py"]
