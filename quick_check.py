#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Final Deployment Readiness Check")
print("=" * 40)

# Check database
db_url = os.getenv('DATABASE_URL', '')
if 'neon' in db_url:
    print("✅ Database: Neon PostgreSQL")
else:
    print("❌ Database: Not Neon")

# Check Redis
redis_url = os.getenv('RATELIMIT_STORAGE_URI', '')
if 'redis' in redis_url:
    print("✅ Rate Limiting: Redis")
else:
    print("❌ Rate Limiting: Not Redis")

# Check security keys
secret_key = os.getenv('SECRET_KEY', '')
jwt_key = os.getenv('JWT_SECRET_KEY', '')

if len(secret_key) >= 32:
    print("✅ SECRET_KEY: Configured")
else:
    print("❌ SECRET_KEY: Missing/Short")

if len(jwt_key) >= 32:
    print("✅ JWT_SECRET_KEY: Configured")
else:
    print("❌ JWT_SECRET_KEY: Missing/Short")

# Final status
all_ready = all([
    'neon' in db_url,
    'redis' in redis_url,
    len(secret_key) >= 32,
    len(jwt_key) >= 32
])

print("\n" + "=" * 40)
if all_ready:
    print("🎉 PROJECT IS READY FOR DEPLOYMENT!")
    print("✅ Neon PostgreSQL Database")
    print("✅ Redis Rate Limiting")
    print("✅ Security Keys Configured")
    print("✅ Production Configuration Complete")
else:
    print("⚠️  PROJECT NEEDS CONFIGURATION")
    print("Please check your .env file")
