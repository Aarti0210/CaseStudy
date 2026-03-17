#!/usr/bin/env python3
"""Verify security keys are properly configured"""

from app import create_app

def verify_keys():
    app = create_app()
    
    secret_key = app.config.get('SECRET_KEY', '')
    jwt_secret_key = app.config.get('JWT_SECRET_KEY', '')
    
    print("🔒 Security Key Verification")
    print("=" * 40)
    print(f"SECRET_KEY: {secret_key[:10]}...{secret_key[-10:]} (Length: {len(secret_key)})")
    print(f"JWT_SECRET_KEY: {jwt_secret_key[:10]}...{jwt_secret_key[-10:]} (Length: {len(jwt_secret_key)})")
    print()
    
    # Check security requirements
    issues = []
    
    if len(secret_key) < 32:
        issues.append(f"SECRET_KEY too short: {len(secret_key)} < 32")
    
    if len(jwt_secret_key) < 32:
        issues.append(f"JWT_SECRET_KEY too short: {len(jwt_secret_key)} < 32")
    
    if issues:
        print("⚠️  Security Issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ All security keys meet requirements!")
        return True

if __name__ == "__main__":
    verify_keys()
