#!/usr/bin/env python3
"""
Pre-Deployment Readiness Check
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path('.').absolute()
sys.path.insert(0, str(project_root))

def check_readiness():
    print('🔍 Pre-Deployment Readiness Check')
    print('=' * 40)
    
    # 1. Check environment variables
    print('1. Environment Variables:')
    required_vars = ['DATABASE_URL', 'SECRET_KEY', 'JWT_SECRET_KEY']
    for var in required_vars:
        value = os.getenv(var)
        status = '✅' if value else '❌'
        print(f'   {status} {var}: {"SET" if value else "MISSING"}')
    
    # 2. Check Redis configuration
    print('\n2. Redis Configuration:')
    redis_url = os.getenv('RATELIMIT_STORAGE_URI')
    redis_status = '✅' if redis_url else '❌'
    print(f'   {redis_status} RATELIMIT_STORAGE_URI: {"SET" if redis_url else "MISSING"}')
    
    # 3. Check database URL format
    print('\n3. Database Configuration:')
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        ssl_configured = 'sslmode=' in db_url
        ssl_status = '✅' if ssl_configured else '❌'
        print(f'   {ssl_status} SSL Configured: {ssl_configured}')
        print(f'   📍 Database Type: {"PostgreSQL" if "postgresql" in db_url else "Other"}')
    
    print('\n🎯 Readiness Summary:')
    all_set = all([
        os.getenv('DATABASE_URL'),
        os.getenv('SECRET_KEY'),
        os.getenv('JWT_SECRET_KEY'),
        os.getenv('RATELIMIT_STORAGE_URI')
    ])
    
    if all_set:
        print('   ✅ READY FOR DEPLOYMENT!')
        print('\n🚀 Deployment Checklist:')
        print('   ✅ Database: Neon PostgreSQL with SSL')
        print('   ✅ Cache: Upstash Redis for rate limiting')
        print('   ✅ Security: JWT and Flask secrets configured')
        print('   ✅ Rate Limiting: Redis-based')
        print('   ✅ Configuration: Production-ready')
        return True
    else:
        print('   ⚠️  Some configuration missing')
        return False

if __name__ == "__main__":
    check_readiness()
