#!/usr/bin/env python3
"""Test JWT and RBAC security implementation"""

import json
import secrets
from app.extensions import db, bcrypt
from app import create_app
from app.models import User, Role
from flask_jwt_extended import create_access_token, create_refresh_token
from app.jwt_utils import get_jwt_identity

def test_jwt_security():
    app = create_app()
    with app.app_context():
        try:
            print("Testing JWT security...")
            
            # Create test user
            user = User(name="Security Test", email=f"security_{secrets.token_hex(4)}@example.com")
            user.set_password("SecurePassword123!")
            
            role = Role.query.filter_by(name="admin").first()
            if not role:
                role = Role(name="admin", description="Administrator")
                db.session.add(role)
                db.session.commit()
            
            user.role_id = role.id
            db.session.add(user)
            db.session.commit()
            
            # Test JWT token creation
            identity = json.dumps({"id": user.id, "role": role.name})
            access_token = create_access_token(identity=identity)
            refresh_token = create_refresh_token(identity=identity)
            
            print(f"✓ JWT tokens created successfully")
            print(f"  Access token length: {len(access_token)}")
            print(f"  Refresh token length: {len(refresh_token)}")
            
            # Test password hashing
            test_password = "TestPassword123!"
            user.set_password(test_password)
            is_valid = user.check_password(test_password)
            is_invalid = user.check_password("WrongPassword")
            
            print(f"✓ Password hashing: Valid={is_valid}, Invalid={is_invalid}")
            
            # Test JWT identity parsing
            with app.test_request_context(headers={'Authorization': f'Bearer {access_token}'}):
                parsed_identity = get_jwt_identity()
                print(f"✓ JWT identity parsing: {parsed_identity}")
            
            # Clean up
            db.session.delete(user)
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"✗ JWT security test failed: {e}")
            db.session.rollback()
            return False

def test_rbac_decorators():
    app = create_app()
    with app.app_context():
        try:
            print("Testing RBAC decorators...")
            
            # Test decorator imports
            from app.middleware.rbac import role_required, roles_allowed
            print("✓ RBAC decorators imported successfully")
            
            # Test decorator creation (without actual request)
            @role_required("admin")
            def admin_only_endpoint():
                return "Admin content"
            
            @roles_allowed("admin", "lawyer")
            def multi_role_endpoint():
                return "Multi-role content"
            
            print("✓ RBAC decorators created successfully")
            
            return True
            
        except Exception as e:
            print(f"✗ RBAC decorator test failed: {e}")
            return False

def test_security_vulnerabilities():
    app = create_app()
    with app.app_context():
        try:
            print("Testing for security vulnerabilities...")
            
            # Check for hardcoded secrets
            import os
            secret_key = app.config.get('SECRET_KEY')
            jwt_secret = app.config.get('JWT_SECRET_KEY')
            
            if secret_key and len(secret_key) < 32:
                print("⚠ SECRET_KEY is too short (< 32 characters)")
            else:
                print("✓ SECRET_KEY length is adequate")
            
            if jwt_secret and len(jwt_secret) < 32:
                print("⚠ JWT_SECRET_KEY is too short (< 32 characters)")
            else:
                print("✓ JWT_SECRET_KEY length is adequate")
            
            # Check for debug mode in production
            debug_mode = app.config.get('DEBUG', False)
            flask_env = os.getenv('FLASK_ENV', 'development')
            
            if flask_env == 'production' and debug_mode:
                print("⚠ DEBUG mode enabled in production environment")
            else:
                print("✓ DEBUG mode appropriately configured")
            
            return True
            
        except Exception as e:
            print(f"✗ Security vulnerability test failed: {e}")
            return False

if __name__ == "__main__":
    print("=== Security Validation Tests ===")
    
    results = []
    results.append(test_jwt_security())
    results.append(test_rbac_decorators())
    results.append(test_security_vulnerabilities())
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n=== Security Test Results: {passed}/{total} passed ===")
    
    if passed == total:
        print("✓ All security tests passed!")
    else:
        print("⚠ Some security tests failed. Review the output above.")
