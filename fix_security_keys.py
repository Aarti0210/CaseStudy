#!/usr/bin/env python3
"""
Security Key Generation Script
Generate secure keys for production deployment
"""

import secrets
import os
from pathlib import Path

def generate_secure_keys():
    """Generate secure keys for JWT and Flask"""
    
    # Generate 32-byte (256-bit) secure keys
    jwt_secret = secrets.token_urlsafe(32)
    flask_secret = secrets.token_urlsafe(32)
    
    print("=== SECURITY KEY GENERATION ===")
    print(f"JWT_SECRET_KEY={jwt_secret}")
    print(f"SECRET_KEY={flask_secret}")
    print()
    print("Key Information:")
    print(f"JWT Secret Length: {len(jwt_secret)} characters")
    print(f"Flask Secret Length: {len(flask_secret)} characters")
    print(f"Both keys meet minimum 32-character requirement")
    print()
    
    return jwt_secret, flask_secret

def update_env_file(jwt_secret, flask_secret):
    """Update .env file with new secure keys"""
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    # Backup existing .env if it exists
    if env_file.exists():
        backup_file = Path(".env.backup")
        env_file.rename(backup_file)
        print(f"✓ Backed up existing .env to {backup_file}")
    
    # Create new .env file
    env_content = f"""# Production Environment Configuration
# Generated on: {__import__('datetime').datetime.now().isoformat()}

# ==========================================
# Flask Configuration
# ==========================================
FLASK_ENV=production
FLASK_APP=run:app
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5000
DEBUG=false
LOG_LEVEL=INFO

# ==========================================
# Security Keys (SECURE - DO NOT SHARE)
# ==========================================
JWT_SECRET_KEY={jwt_secret}
SECRET_KEY={flask_secret}

# ==========================================
# Database Configuration
# ==========================================
# Set your production database URL here
DATABASE_URL=postgresql://user:password@localhost:5432/judicial_supreme

# ==========================================
# OpenAI API
# ==========================================
OPENAI_API_KEY=your-openai-api-key-here

# ==========================================
# Rate Limiting (Production)
# ==========================================
RATELIMIT_STORAGE_URI=redis://localhost:6379/0

# ==========================================
# Email Configuration (for OTP)
# ==========================================
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=no-reply@judicial.local

# ==========================================
# Upload Configuration
# ==========================================
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# ==========================================
# JWT Configuration
# ==========================================
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=86400

# ==========================================
# OTP Configuration
# ==========================================
OTP_TTL=300
OTP_RESEND_COOLDOWN=60
OTP_SEND_MAX_RETRIES=3
"""
    
    env_file.write_text(env_content)
    print(f"✓ Created new .env file with secure keys")
    print(f"⚠️  Please update DATABASE_URL and other settings in .env")
    
    return True

def validate_key_strength(key):
    """Validate key strength requirements"""
    
    issues = []
    
    if len(key) < 32:
        issues.append(f"Key too short: {len(key)} < 32 characters")
    
    if not any(c.isupper() for c in key):
        issues.append("No uppercase letters")
    
    if not any(c.islower() for c in key):
        issues.append("No lowercase letters")
    
    if not any(c.isdigit() for c in key):
        issues.append("No digits")
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in key):
        issues.append("No special characters")
    
    return issues

def main():
    """Main execution"""
    
    print("Judicial Supreme Backend - Security Key Generator")
    print("=" * 50)
    
    # Generate keys
    jwt_secret, flask_secret = generate_secure_keys()
    
    # Validate key strength
    jwt_issues = validate_key_strength(jwt_secret)
    flask_issues = validate_key_strength(flask_secret)
    
    if jwt_issues or flask_issues:
        print("⚠️  Key Strength Issues:")
        for issue in jwt_issues:
            print(f"  JWT: {issue}")
        for issue in flask_issues:
            print(f"  Flask: {issue}")
    else:
        print("✅ Both keys meet strength requirements")
    
    # Ask user if they want to update .env
    response = input("\nUpdate .env file with new keys? (y/n): ").lower().strip()
    
    if response == 'y':
        update_env_file(jwt_secret, flask_secret)
        print("\n✅ Security keys generated and .env file updated")
        print("🔒 Please keep these keys secure and do not commit to version control")
    else:
        print("\nKeys generated but .env file not updated")
        print("Add these keys manually to your environment configuration:")
        print(f"JWT_SECRET_KEY={jwt_secret}")
        print(f"SECRET_KEY={flask_secret}")
    
    print("\n=== Next Steps ===")
    print("1. Update DATABASE_URL in .env")
    print("2. Set up Redis for rate limiting")
    print("3. Configure email service for OTP")
    print("4. Set OpenAI API key")
    print("5. Test the application with new keys")

if __name__ == "__main__":
    main()
