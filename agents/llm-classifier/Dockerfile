FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY service.py .

# Copy shared modules from parent directory
COPY ../llm_classifier.py .
COPY ../cache_manager.py .
COPY ../ai_config.py .

# Expose port
EXPOSE 8005

# Run service
CMD ["python", "service.py"]
