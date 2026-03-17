# 🔐 Environment Variables Guide

## 📋 **Complete Environment Variable Reference**

### **Required Variables** 🔴
These must be set for the application to run:

```bash
# Security (Required)
SECRET_KEY=your-32-char-secret-key-here
JWT_SECRET_KEY=your-32-char-jwt-secret-here

# Database (Required)
DATABASE_URL=postgresql://user:password@host:5432/database_name

# Flask Environment (Required)
FLASK_ENV=production
```

---

### **Optional Variables** 🟡
Enhance functionality when set:

```bash
# Application Settings
DEBUG=false
LOG_LEVEL=INFO
PORT=5000

# Gunicorn Settings
GUNICORN_WORKERS=1
GUNICORN_TIMEOUT=120

# AI Services
OPENAI_API_KEY=sk-your-openai-api-key-here
AI_TIMEOUT_SECONDS=30
AI_MAX_TOKENS=4000

# Email Services (for OTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=no-reply@judicial.local

# Rate Limiting
RATELIMIT_STORAGE_URI=redis://localhost:6379/0
```

---

## 🚀 **Quick Setup Commands**

### **Generate New Secrets**
```bash
# Generate all security keys
python scripts/env_manager_cli.py generate --all

# Generate specific secret
python scripts/env_manager_cli.py set SECRET_KEY
```

### **Show Current Configuration**
```bash
python scripts/env_manager_cli.py show
```

### **Validate Environment**
```bash
python scripts/env_manager_cli.py validate
```

### **List All Variables**
```bash
python scripts/env_manager_cli.py list
```

### **Add Variable**
```bash
python scripts/env_manager_cli.py add VARIABLE_NAME "variable_value"
```

---

## 🗄️ **Database URLs by Platform**

### **Render (Production)**
```bash
# Format from Render PostgreSQL service
DATABASE_URL=postgresql://case_database_user:oYqxCbvitwwpscTeRKdGretEIW0fuzHO@dpg-d6o09rfkijhs739uq5sg-a.oregon-postgres.render.com/case_database
```

### **Local Development**
```bash
# SQLite for local development
DATABASE_URL=sqlite:///judicial_supreme_dev.db

# PostgreSQL local
DATABASE_URL=postgresql://user:password@localhost:5432/judicial_supreme
```

### **AWS RDS**
```bash
# AWS RDS PostgreSQL
DATABASE_URL=postgresql://username:password@rds-endpoint.amazonaws.com:5432/database_name
```

### **Heroku**
```bash
# Heroku PostgreSQL
DATABASE_URL=postgresql://username:password@host:5432/database_name?sslmode=require
```

---

## 🔐 **Security Keys Generation**

### **Generate Secure Keys**
```bash
# Method 1: Python secrets (Recommended)
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Method 2: OpenSSL
openssl rand -base64 32

# Method 3: Using our CLI tool
python scripts/env_manager_cli.py generate --all
```

### **Security Requirements**
- **SECRET_KEY**: Minimum 32 characters
- **JWT_SECRET_KEY**: Minimum 32 characters
- **Never commit** secrets to version control
- **Use environment variables** in production

---

## 🚀 **Environment Setup by Platform**

### **Render Deployment**
```bash
# Quick setup with your database URL
python scripts/env_setup.py --type render --database-url "postgresql://case_database_user:oYqxCbvitwwpscTeRKdGretEIW0fuzHO@dpg-d6o09rfkijhs739uq5sg-a.oregon-postgres.render.com/case_database"

# This creates:
# - .env file with all variables
# - render.yaml for deployment
# - Secure keys generated automatically
```

### **Local Development**
```bash
# Setup development environment
python scripts/env_setup.py --type development

# Creates .env with SQLite and debug mode
```

### **Production Server**
```bash
# Setup production environment
python scripts/env_setup.py --type production

# Creates .env with PostgreSQL settings
```

---

## 🔧 **Environment Variable Access in Code**

### **Using EnvManager (Recommended)**
```python
from app.env_manager import EnvManager

# Get required variable
secret_key = EnvManager.get_required('SECRET_KEY')

# Get optional variable with default
debug = EnvManager.get_optional('DEBUG', False)

# Get boolean
debug = EnvManager.get_bool('DEBUG', False)

# Get integer
port = EnvManager.get_int('PORT', 5000)

# Get configuration groups
security = EnvManager.get_security_config()
database = EnvManager.get_database_config()
```

### **Direct os.getenv (Legacy)**
```python
import os

# Direct access (not recommended)
secret_key = os.getenv('SECRET_KEY')
```

---

## 🔍 **Environment Validation**

### **Check Required Variables**
```bash
# Validate all required variables are set
python scripts/env_manager_cli.py validate

# Expected output:
# ✅ All required variables are set
# OR
# ❌ Missing: SECRET_KEY, DATABASE_URL
```

### **Show Current State**
```bash
# Show complete environment status
python scripts/env_manager_cli.py show

# Shows:
# - Security keys status
# - Database connection
# - Optional services
# - Configuration values
```

---

## 📱 **Platform-Specific Variables**

### **Render Environment Variables**
```bash
# Automatically set by Render
# RENDER_SERVICE_NAME
# RENDER_SERVICE_ID
# RENDER_EXTERNAL_URL
# RENDER_EXTERNAL_HOSTNAME

# Common Render patterns
DATABASE_URL=postgresql://user:password@host:5432/db
PORT=8000
GUNICORN_WORKERS=1
```

### **Docker Environment**
```bash
# Set in Dockerfile
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PYTHONDONTWRITEBYTECODE=1
```

### **GitHub Actions**
```yaml
# .github/workflows/deploy.yml
env:
  SECRET_KEY: ${{ secrets.SECRET_KEY }}
  JWT_SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }}
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

---

## 🛡️ **Security Best Practices**

### **Never Commit Secrets**
```bash
# .gitignore should include:
.env
.env.local
.env.*.key
secrets/
```

### **Use Different Keys per Environment**
```bash
# Development
SECRET_KEY=dev-secret-key-here
JWT_SECRET_KEY=dev-jwt-secret-here

# Production
SECRET_KEY=prod-secret-key-here
JWT_SECRET_KEY=prod-jwt-secret-here
```

### **Rotate Keys Regularly**
```bash
# Generate new keys
python scripts/env_manager_cli.py generate --all

# Update in deployment platform
```

---

## 📊 **Environment Debugging**

### **Common Issues**
1. **Database connection failed** → Check DATABASE_URL format
2. **Import errors** → Verify .env file exists
3. **Permission denied** → Check file permissions
4. **Variable not found** → Use validate command

### **Debug Commands**
```bash
# Show all variables
python scripts/env_manager_cli.py show

# Test database connection
python scripts/test_db_connection.py

# Validate configuration
python scripts/env_manager_cli.py validate
```

---

## 🎯 **Quick Reference**

| Variable | Required | Default | Description |
|----------|-----------|---------|-------------|
| SECRET_KEY | ✅ | None | Flask secret key |
| JWT_SECRET_KEY | ✅ | None | JWT signing key |
| DATABASE_URL | ✅ | None | Database connection |
| FLASK_ENV | ✅ | None | Flask environment |
| DEBUG | ❌ | False | Debug mode |
| LOG_LEVEL | ❌ | INFO | Logging level |
| PORT | ❌ | 5000 | Server port |
| OPENAI_API_KEY | ❌ | None | OpenAI API key |
| MAIL_SERVER | ❌ | None | SMTP server |
| GUNICORN_WORKERS | ❌ | 1 | Worker count |

---

## 🚀 **You're Ready!**

Use this guide to:
- ✅ Set up environment variables
- ✅ Generate secure secrets
- ✅ Configure for any platform
- ✅ Validate your setup
- ✅ Deploy with confidence

**Your Judicial Supreme Backend environment management is complete!** 🎉
