# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all model files and application code
COPY *.pkl .
COPY *.keras .
COPY app.py .

# Expose port 5001
EXPOSE 5001

# Run the application
CMD ["python", "app.py"]
