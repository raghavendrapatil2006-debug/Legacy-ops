FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_NAME="0.0.0.0"

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . /app/
EXPOSE 7860

# Updated to point to the new server folder
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]