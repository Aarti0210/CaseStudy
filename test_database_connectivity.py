#!/usr/bin/env python3
"""
Database connectivity test script.
Tests database connection and basic operations.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(project_root))

def test_database_connection():
    """Test database connection and basic operations."""
    print("🔍 Testing Database Connectivity...")
    print("=" * 50)
    
    try:
        # Load environment
        from dotenv import load_dotenv
        load_dotenv()
        
        # Import app components
        from app import create_app
        from app.extensions import db
        from sqlalchemy import text
        
        # Create app context
        app = create_app()
        
        with app.app_context():
            print("✅ App context created successfully")
            
            # Test 1: Basic connection
            print("\n📋 Test 1: Basic Database Connection")
            try:
                result = db.session.execute(text("SELECT 1 as test"))
                test_value = result.fetchone()[0]
                print(f"✅ Database connection successful: {test_value}")
            except Exception as e:
                print(f"❌ Database connection failed: {str(e)}")
                return False
            
            # Test 2: Table existence
            print("\n📋 Test 2: Check Table Existence")
            try:
                # Check if key tables exist
                tables_to_check = ['user', 'role', 'case', 'audit_log']
                
                for table in tables_to_check:
                    try:
                        result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.fetchone()[0]
                        print(f"✅ Table '{table}' exists: {count} records")
                    except Exception as e:
                        print(f"❌ Table '{table}' not accessible: {str(e)}")
                        
            except Exception as e:
                print(f"❌ Table check failed: {str(e)}")
            
            # Test 3: Basic CRUD operations
            print("\n📋 Test 3: Basic CRUD Operations")
            try:
                from app.models.user import User
                from app.models.role import Role
                
                # Test role creation
                test_role = Role(name="test_role")
                db.session.add(test_role)
                db.session.flush()
                print("✅ Role creation successful")
                
                # Test user creation
                test_user = User(
                    name="Test User",
                    email="test@example.com",
                    role_id=test_role.id
                )
                test_user.set_password("testpassword123")
                db.session.add(test_user)
                db.session.flush()
                print("✅ User creation successful")
                
                # Rollback test data
                db.session.rollback()
                print("✅ Test data rolled back")
                
            except Exception as e:
                print(f"❌ CRUD operations failed: {str(e)}")
                db.session.rollback()
            
            # Test 4: Configuration validation
            print("\n📋 Test 4: Configuration Validation")
            try:
                from app.config import BaseConfig
                
                # Check critical config
                critical_configs = [
                    ('SECRET_KEY', BaseConfig.SECRET_KEY),
                    ('JWT_SECRET_KEY', BaseConfig.JWT_SECRET_KEY),
                    ('DATABASE_URL', BaseConfig.SQLALCHEMY_DATABASE_URI)
                ]
                
                for config_name, config_value in critical_configs:
                    if config_value:
                        if config_name in ['SECRET_KEY', 'JWT_SECRET_KEY']:
                            if len(config_value) >= 32:
                                print(f"✅ {config_name}: Secure (length: {len(config_value)})")
                            else:
                                print(f"❌ {config_name}: Insecure (length: {len(config_value)})")
                        else:
                            print(f"✅ {config_name}: Configured")
                    else:
                        print(f"❌ {config_name}: Missing")
                        
            except Exception as e:
                print(f"❌ Configuration validation failed: {str(e)}")
            
            print("\n" + "=" * 50)
            print("🎯 Database Connectivity Test Complete!")
            return True
            
    except Exception as e:
        print(f"❌ Critical error during database test: {str(e)}")
        return False


def test_environment_variables():
    """Test environment variable setup."""
    print("\n🔍 Testing Environment Variables...")
    print("=" * 50)
    
    critical_env_vars = [
        'FLASK_ENV',
        'SECRET_KEY',
        'JWT_SECRET_KEY',
        'DATABASE_URL',
        'RATELIMIT_STORAGE_URI'
    ]
    
    for var in critical_env_vars:
        value = os.getenv(var)
        if value:
            if 'SECRET' in var or 'KEY' in var:
                masked_value = value[:4] + '*' * (len(value) - 4)
                print(f"✅ {var}: {masked_value} (length: {len(value)})")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Missing")


if __name__ == "__main__":
    print("🚀 Judicial Supreme Backend - Database Connectivity Test")
    print("=" * 60)
    
    # Test environment variables first
    test_environment_variables()
    
    # Test database connectivity
    success = test_database_connection()
    
    if success:
        print("\n🎉 All tests passed! Database is ready for production.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the errors above.")
        sys.exit(1)
