# Mental Health Bot Dockerfile
# Multi-stage build for smaller image size

FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt . 

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY .  .

# Create logs directory
RUN mkdir -p /app/logs

# The volume mount overwrites directory permissions

# Health check (optional)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pgrep -f "python bot.py" || exit 1

# Create data directory at runtime and start bot
CMD ["sh", "-c", "mkdir -p /app/data && chmod 777 /app/data && python bot.py"]
