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

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . /app

# Create necessary directories
RUN mkdir -p /app/uploads /app/logs

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# ✅ FIXED Gunicorn command - USING CORRECT run:app
# Force rebuild: 2026-03-21-12:41
CMD ["gunicorn", "run:app", "--workers", "2", "--worker-class", "gthread", "--threads", "4", "--timeout", "120", "--bind", "0.0.0.0:8000"]