# Use the official Python 3.10 slim image for a lightweight footprint
FROM python:3.10-slim

# Set environment variables to ensure Python output is logged immediately
# and to force Gradio to listen on all network interfaces
ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_NAME="0.0.0.0"

# Install system dependencies (Git is often required for certain Python packages)
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker caching
COPY requirements.txt /app/

# Upgrade pip and install the Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
# (This includes src/, assets/, app.py, etc.)
COPY . /app/

# Expose port 7860, which is the default for Gradio
EXPOSE 7860

# Command to run the application
CMD ["python", "app.py"]