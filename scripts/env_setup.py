#!/usr/bin/env python3
"""
Environment Setup Script
Sets up and validates environment variables for different deployment targets
"""

import os
import secrets
import argparse
from pathlib import Path

def generate_secrets():
    """Generate secure secret keys"""
    jwt_secret = secrets.token_urlsafe(32)
    flask_secret = secrets.token_urlsafe(32)
    
    return {
        'JWT_SECRET_KEY': jwt_secret,
        'SECRET_KEY': flask_secret
    }

def create_env_file(env_type: str, database_url: str = None):
    """Create environment file for specific deployment type"""
    
    if env_type == 'render':
        env_content = f"""# Render Environment Configuration
# Generated for Judicial Supreme Backend deployment

# ==========================================
# Flask Configuration
# ==========================================
FLASK_ENV=production
DEBUG=false
LOG_LEVEL=INFO
PORT=8000

# ==========================================
# Security Keys (Auto-generated)
# ==========================================
JWT_SECRET_KEY={generate_secrets()['JWT_SECRET_KEY']}
SECRET_KEY={generate_secrets()['SECRET_KEY']}

# ==========================================
# Database Configuration
# ==========================================
DATABASE_URL={database_url or 'postgresql://user:password@localhost:5432/judicial_supreme'}

# ==========================================
# Gunicorn Configuration
# ==========================================
GUNICORN_WORKERS=1
GUNICORN_TIMEOUT=120

# ==========================================
# AI Services (Optional)
# ==========================================
OPENAI_API_KEY=
AI_TIMEOUT_SECONDS=30
AI_MAX_TOKENS=4000

# ==========================================
# Email Services (Optional)
# ==========================================
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=no-reply@judicial.local

# ==========================================
# Rate Limiting
# ==========================================
RATELIMIT_STORAGE_URI=
"""
    
    elif env_type == 'development':
        env_content = f"""# Development Environment Configuration
# Generated for Judicial Supreme Backend

# ==========================================
# Flask Configuration
# ==========================================
FLASK_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
PORT=5000

# ==========================================
# Security Keys
# ==========================================
JWT_SECRET_KEY={generate_secrets()['JWT_SECRET_KEY']}
SECRET_KEY={generate_secrets()['SECRET_KEY']}

# ==========================================
# Database Configuration
# ==========================================
DATABASE_URL=sqlite:///judicial_supreme_dev.db

# ==========================================
# AI Services
# ==========================================
OPENAI_API_KEY=
AI_TIMEOUT_SECONDS=30
AI_MAX_TOKENS=4000
"""
    
    elif env_type == 'production':
        env_content = f"""# Production Environment Configuration
# Generated for Judicial Supreme Backend

# ==========================================
# Flask Configuration
# ==========================================
FLASK_ENV=production
DEBUG=false
LOG_LEVEL=INFO
PORT=5000

# ==========================================
# Security Keys
# ==========================================
JWT_SECRET_KEY={generate_secrets()['JWT_SECRET_KEY']}
SECRET_KEY={generate_secrets()['SECRET_KEY']}

# ==========================================
# Database Configuration
# ==========================================
DATABASE_URL=postgresql://user:password@localhost:5432/judicial_supreme

# ==========================================
# AI Services
# ==========================================
OPENAI_API_KEY=
AI_TIMEOUT_SECONDS=30
AI_MAX_TOKENS=4000
"""
    
    else:
        raise ValueError(f"Unknown environment type: {env_type}")
    
    return env_content

def setup_render_env(database_url: str):
    """Setup environment for Render deployment"""
    print("🚀 Setting up Render Environment")
    print("=" * 35)
    
    # Create .env file
    env_content = create_env_file('render', database_url)
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created for Render deployment")
    print(f"🔑 Generated new security keys")
    print(f"🗄️  Database URL: {database_url.split('@')[1] if '@' in database_url else 'Set'}")
    
    # Create render.yaml
    render_yaml = f"""# Render Deployment Configuration
service:
  name: judicial-supreme-backend
  type: web
  env: docker
  region: oregon
  plan: free

build:
  dockerfilePath: ./Dockerfile
  dockerContext: .

runtime:
  startCommand: gunicorn -k eventlet -w ${{GUNICORN_WORKERS:-1}} run:app
  healthCheckPath: /health
  healthCheckTimeout: 30
  healthCheckInterval: 10
  healthCheckGracePeriod: 60

environment:
  FLASK_ENV: production
  SECRET_KEY: {generate_secrets()['SECRET_KEY']}
  JWT_SECRET_KEY: {generate_secrets()['JWT_SECRET_KEY']}
  DATABASE_URL: {database_url}
  GUNICORN_WORKERS: 1
  LOG_LEVEL: INFO

database:
  name: judicial-supreme-db
  type: postgres
  plan: free
  databaseName: judicial_supreme
  user: judicial_user
"""
    
    with open('render.yaml', 'w') as f:
        f.write(render_yaml)
    
    print("✅ render.yaml created for Render deployment")
    
    return True

def setup_development_env():
    """Setup environment for development"""
    print("🔧 Setting up Development Environment")
    print("=" * 35)
    
    env_content = create_env_file('development')
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created for development")
    print("🗄️  Using SQLite database")
    
    return True

def validate_env():
    """Validate current environment"""
    print("🔍 Validating Environment")
    print("=" * 30)
    
    try:
        from app.env_manager import EnvManager
        EnvManager.print_all_configs()
        
        required = EnvManager.validate_required()
        if all(required.values()):
            print("✅ Environment validation passed")
            return True
        else:
            print("❌ Environment validation failed")
            return False
            
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Setup environment for Judicial Supreme Backend')
    parser.add_argument('--type', choices=['render', 'development', 'production'], 
                       help='Environment type to setup')
    parser.add_argument('--database-url', 
                       help='Database URL (required for render)')
    parser.add_argument('--validate', action='store_true',
                       help='Validate current environment')
    
    args = parser.parse_args()
    
    if args.validate:
        validate_env()
    elif args.type == 'render':
        if not args.database_url:
            print("❌ --database-url is required for render setup")
            print("Example: python scripts/env_setup.py --type render --database-url 'postgresql://user:pass@host:5432/db'")
            return
        
        setup_render_env(args.database_url)
    elif args.type == 'development':
        setup_development_env()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
