# Production Deployment Guide

This guide covers deploying the Judicial Supreme Backend as a containerized application using Docker and Docker Compose.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start with Docker Compose](#quick-start-with-docker-compose)
3. [Manual Docker Build & Run](#manual-docker-build--run)
4. [Environment Configuration](#environment-configuration)
5. [Production Deployment](#production-deployment)
6. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
7. [Security Checklist](#security-checklist)

---

## Prerequisites

- **Docker** 20.10+
- **Docker Compose** 2.0+ (for container orchestration)
- **Git** (for cloning repository)

### Verify Installation

```bash
docker --version
docker-compose --version
```

---

## Quick Start with Docker Compose

The easiest way to run the entire stack (backend + PostgreSQL) is with docker-compose.

### Step 1: Clone & Setup

```bash
git clone <repository-url> judicial_backend
cd judicial_backend
```

### Step 2: Configure Environment

```bash
cp .env.example .env
```

**Edit `.env` and set:**
- `JWT_SECRET_KEY` - Generate a secure random 32+ character string:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- `SECRET_KEY` - Another random secure string
- `POSTGRES_PASSWORD` - Strong database password

### Step 3: Build & Start Services

```bash
# Build images and start all services
docker-compose up -d

# Watch logs
docker-compose logs -f backend

# Wait for database to initialize (~10-15 seconds)
```

### Step 4: Verify Deployment

```bash
# Check all services running
docker-compose ps

# Test health endpoint
curl http://localhost:8000/health

# Check backend logs
docker-compose logs backend | tail -20
```

### Step 5: Database Migration (if needed)

```bash
# Run migrations inside container
docker-compose exec backend flask db upgrade
```

::: tip
Default access:
- **Backend API**: http://localhost:8000
- **Health Endpoint**: http://localhost:8000/health
- **PostgreSQL**: localhost:5432 (via host machine)
:::

---

## Manual Docker Build & Run

For more control or CI/CD integration, build and run manually.

### Step 1: Build Docker Image

```bash
# Build with default settings
docker build -t judicial-backend:latest .

# Build with custom build args
docker build \
  -t judicial-backend:latest \
  --build-arg PYTHON_VERSION=3.11 \
  .
```

### Step 2: Create Network (if using separate MySQL)

```bash
docker network create judicial_network
```

### Step 3: Start PostgreSQL (optional - or use external DB)

```bash
docker run -d \
  --name judicial_postgres \
  --network judicial_network \
  -e POSTGRES_USER=appuser \
  -e POSTGRES_PASSWORD=apppassword \
  -e POSTGRES_DB=judicial_supreme \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:16-alpine
```

### Step 4: Run Backend Container

```bash
docker run -d \
  --name judicial_backend \
  --network judicial_network \
  -e FLASK_ENV=production \
  -e DATABASE_URL=postgresql://appuser:apppassword@judicial_postgres:5432/judicial_supreme \
  -e JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))") \
  -e GUNICORN_WORKERS=1 \
  -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/logs:/app/logs \
  judicial-backend:latest
```

**Note on uploads:** On platforms like Render Free, the filesystem is ephemeral;  files will be lost on redeploy. Configure an external object store (S3, GCS) for persistent uploads in production.

### Step 5: Verify

```bash
# Check container is running
docker ps | grep judicial

# View logs
docker logs -f judicial_backend

# Test API
curl http://localhost:8000/health
```

---

## Environment Configuration

### Critical Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `FLASK_ENV` | Deployment environment | `production` |
| `JWT_SECRET_KEY` | JWT signing key (32+ chars) | `secretkey...` |
| `DATABASE_URL` | Database connection string | `postgresql://user:pass@host/db` |
| `GUNICORN_WORKERS` | Number of worker processes | `1` (Render Free), `2` (standard) |
| `DEBUG` | Enable debug mode (always false in prod) | `false` |

### Optional Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI features | `` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `GUNICORN_WORKERS` | Number of Gunicorn workers | `2` |
| `MAIL_SERVER` | SMTP server for email | `` |

### Secrets Management Best Practice

**DO NOT hardcode secrets in .env file for production:**

Use a secrets manager:
- **Docker Secrets** (for Docker Swarm)
- **AWS Secrets Manager** (for AWS deployments)
- **HashiCorp Vault** (for enterprise)
- **Environment variables** via CI/CD pipeline

Example with Docker Secrets:
```bash
docker secret create jwt_secret <(echo "your-secret-here")

# Reference in compose
docker-compose -f docker-compose.prod.yml up
```

---

## Production Deployment

### Docker Compose (Single Server)

```bash
# Pull latest code
git pull origin main

# Rebuild image with latest code
docker-compose build --no-cache

# Update containers gracefully
docker-compose up -d

# Verify health
docker-compose ps
curl http://localhost:8000/health

# View logs
docker-compose logs -f backend
```

### Kubernetes (Scale to Multiple Nodes)

See `kubernetes/` directory for Helm charts and manifests.

```bash
# Build and push image
docker build -t your-registry/judicial-backend:v1.0.0 .
docker push your-registry/judicial-backend:v1.0.0

# Deploy to Kubernetes
kubectl apply -f kubernetes/

# Monitor
kubectl get pods -n judicial-supreme
kubectl logs -f deployment/backend -n judicial-supreme
```

### Cloud Platforms

**AWS ECS/Fargate:**
```bash
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
docker tag judicial-backend:latest <account>.dkr.ecr.<region>.amazonaws.com/judicial-backend:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/judicial-backend:latest
# Use ECS task definition with image URI
```

**Azure Container Instances:**
```bash
az acr build --registry <registry-name> --image judicial-backend:latest .
az container create --resource-group <group> --registry-login-server <server> ...
```

**Google Cloud Run:**
```bash
gcloud builds submit --tag gcr.io/<project>/judicial-backend
gcloud run deploy judicial-backend --image gcr.io/<project>/judicial-backend
```

---

## Render Deployment (Recommended for Free Tier)

**Render** provides managed PostgreSQL and simple deployment:

### Step 1: Create PostgreSQL Database on Render

1. Go to [render.com](https://render.com)
2. Click **New +** → **PostgreSQL**
3. Set name: `judicial-supreme-db`
4. Region: Choose closest region
5. Click **Create Database**
6. Copy the `Internal Database URL` (keep this private)

### Step 2: Create Web Service on Render

1. Click **New +** → **Web Service**
2. Connect your GitHub repository
3. Set name: `judicial-supreme-backend`
4. Environment: `Docker`
5. Region: Same as database (for performance)
6. Build Command: `pip install -r requirements.txt`
7. Start Command: `gunicorn -k eventlet -w 1 run:app`
8. Click **Advanced** and add environment variables:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `DATABASE_URL` | Paste from PostgreSQL service |
| `JWT_SECRET_KEY` | Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `SECRET_KEY` | Generate secure random string |
| `GUNICORN_WORKERS` | `1` |

9. Click **Create Web Service**

### Step 3: Database Migration

After deployment, run migrations once:
```bash
# Via Render Shell console in dashboard
flask db upgrade
```

### Notes on Render Free Tier
- **Storage is ephemeral** - uploaded files deleted on redeploy
- **Single worker** - memory limited to ~512MB
- **Rate limiting** - in-memory store (suitable for small demo projects)
- **Auto-redeploy** - on every git push (recommended for testing)

---

## AWS ECS/Fargate Deployment

### Health Check

```bash
# Local
curl http://localhost:8000/health

# Via Docker
docker exec judicial_backend curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-03-03T12:00:00Z"
}
```

### View Logs

```bash
# Docker Compose
docker-compose logs backend
docker-compose logs backend --tail=100 -f

# Manual Docker
docker logs -f judicial_backend
docker logs --tail 50 judicial_backend

# Inside container
docker exec judicial_backend tail -f /app/logs/app.log
```

### Database Connection Issues

```bash
# Test PostgreSQL connectivity
docker exec judicial_backend psql -h postgres -U appuser -d judicial_supreme -c "SELECT 1"

# Run migrations
docker exec judicial_backend flask db upgrade
```

### Container Restart Issues

```bash
# View detailed logs
docker logs judicial_backend 2>&1 | tail -50

# Restart container
docker restart judicial_backend

# Or with docker-compose
docker-compose restart backend
```

### Performance Tuning

```bash
# Increase Gunicorn workers for high traffic (not recommended for Render Free)
GUNICORN_WORKERS=2 docker-compose up -d

# Monitor container resource usage
docker stats

# Check database connection health
docker exec judicial_backend psql -h postgres -U appuser -d judicial_supreme -c "SELECT datname, count(*) as connection_count FROM pg_stat_activity GROUP BY datname;"
```

---

## Security Checklist

### Before Production Deployment

- [ ] Change `JWT_SECRET_KEY` to cryptographically secure 32+ character string
- [ ] Change `POSTGRES_PASSWORD` to strong database password
- [ ] Change `SECRET_KEY` to secure random string
- [ ] Set `DEBUG=false`
- [ ] Set `FLASK_ENV=production`
- [ ] Remove or secure any hardcoded secrets from `.env` (use secrets manager)
- [ ] Use HTTPS/TLS in reverse proxy (Nginx, load balancer)
- [ ] Enable database encryption at rest (Render handles this)
- [ ] Configure firewall rules (only expose port 8000 to load balancer)
- [ ] Enable audit logging
- [ ] Set up monitoring and alerting
- [ ] Regular backup of PostgreSQL database
- [ ] Image scanning for vulnerabilities:
  ```bash
  docker scan judicial-backend:latest
  ```

### Runtime Security

```bash
# Run as non-root user (already configured in Dockerfile)
docker run --user appuser judicial-backend:latest

# Use read-only filesystem where possible
docker run --read-only judicial-backend:latest

# Limit resources
docker run --memory 1g --cpus 0.5 judicial-backend:latest

# Drop unnecessary capabilities
docker run --cap-drop ALL judicial-backend:latest
```

### Dependency Updates

```bash
# Check for security vulnerabilities in Python packages
pip-audit

# Update dependencies (in development)
pip install --upgrade pip
pip install -r requirements.txt --upgrade

# Rebuild Docker image with latest base image
docker build --no-cache -t judicial-backend:latest .
```

---

## Useful Commands

```bash
# Docker Compose
docker-compose up -d              # Start services
docker-compose down               # Stop and remove services
docker-compose restart            # Restart all services
docker-compose build --no-cache   # Rebuild images
docker-compose exec backend bash  # Shell into backend container
docker-compose logs -f backend    # Stream logs

# Docker (manual)
docker build -t name:tag .        # Build image
docker run -d --name container .  # Run container
docker stop container             # Stop container
docker logs -f container          # View logs
docker inspect container          # View configuration
docker prune                       # Clean up unused images/containers
```

---

## Support & Troubleshooting

For issues:
1. Check logs: `docker-compose logs backend`
2. Verify environment variables: `docker-compose exec backend env | grep FLASK`
3. Test connectivity: `docker-compose exec backend curl http://localhost:8000/health`
4. Check database: `docker-compose exec mysql mysql -u root -p`

---

**Last Updated:** March 2026
**Version:** 1.0.0
