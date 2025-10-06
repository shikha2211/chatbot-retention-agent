# Use a slim Python image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# System deps (install build tools only if needed by deps)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better layer caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir python-dotenv

# Copy application source
COPY . /app

# Default environment configuration
ENV HOST=0.0.0.0 \
    PORT=9000 \
    RELOAD=false

# Expose FastAPI port
EXPOSE 9000

# Start the FastAPI server
CMD ["python", "start_server.py"]
