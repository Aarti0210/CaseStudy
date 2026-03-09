FROM python:3.11-slim

WORKDIR /app

# Set environment variables - Python optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    FLASK_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies (no cache for better security)
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code (exclude .env via .dockerignore)
COPY . /app

# Create uploads and logs directories with correct permissions
RUN mkdir -p /app/uploads /app/logs

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port for Gunicorn
EXPOSE 8000

# Health check - verifies app is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run Gunicorn with eventlet worker
# - eventlet: enables async/WebSocket support for Flask-SocketIO
# - workers: configurable via GUNICORN_WORKERS env var (default 1 for Render Free)
# - bind: 0.0.0.0:8000 for container networking
# - timeout: 120s to allow long-running ML predictions
CMD exec gunicorn \
    --worker-class eventlet \
    --workers ${GUNICORN_WORKERS:-1} \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    run:app
