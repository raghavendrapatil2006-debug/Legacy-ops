# Use the official Python 3.10 slim image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_NAME="0.0.0.0"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements first for Docker caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Expose port
EXPOSE 7860

# Command to run the application using Uvicorn (FastAPI)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]