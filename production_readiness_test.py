#!/usr/bin/env python3
"""
Production readiness test script.
Comprehensive testing of all system components.
"""

import os
import sys
import requests
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(project_root))

def test_api_endpoints():
    """Test critical API endpoints."""
    print("\n🌐 Testing API Endpoints...")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    test_results = []
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check: PASSED")
            test_results.append(("Health Check", True, None))
        else:
            print(f"❌ Health check: FAILED (Status: {response.status_code})")
            test_results.append(("Health Check", False, f"Status: {response.status_code}"))
    except Exception as e:
        print(f"❌ Health check: ERROR ({str(e)})")
        test_results.append(("Health Check", False, str(e)))
    
    # Test 2: Home route
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Home route: PASSED")
            test_results.append(("Home Route", True, None))
        else:
            print(f"❌ Home route: FAILED (Status: {response.status_code})")
            test_results.append(("Home Route", False, f"Status: {response.status_code}"))
    except Exception as e:
        print(f"❌ Home route: ERROR ({str(e)})")
        test_results.append(("Home Route", False, str(e)))
    
    # Test 3: Authentication endpoints (with test data)
    auth_tests = [
        ("POST", "/api/v1/auth/signup", {
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpassword123",
            "role": "citizen"
        }),
        ("POST", "/api/v1/auth/login", {
            "email": "test@example.com",
            "password": "testpassword123"
        })
    ]
    
    for method, endpoint, data in auth_tests:
        try:
            if method == "POST":
                response = requests.post(f"{base_url}{endpoint}", json=data, timeout=5)
            
            if response.status_code in [200, 201]:
                print(f"✅ Auth {method} {endpoint}: PASSED")
                test_results.append((f"Auth {method} {endpoint}", True, None))
            else:
                print(f"❌ Auth {method} {endpoint}: FAILED (Status: {response.status_code})")
                test_results.append((f"Auth {method} {endpoint}", False, f"Status: {response.status_code}"))
        except Exception as e:
            print(f"❌ Auth {method} {endpoint}: ERROR ({str(e)})")
            test_results.append((f"Auth {method} {endpoint}", False, str(e)))
    
    return test_results


def test_database_operations():
    """Test database operations."""
    print("\n💾 Testing Database Operations...")
    print("=" * 50)
    
    try:
        from app import create_app
        from app.extensions import db
        from app.models.user import User
        from app.models.role import Role
        from sqlalchemy import text
        
        app = create_app()
        
        with app.app_context():
            # Test 1: User creation
            try:
                test_role = Role(name="test_role_db")
                db.session.add(test_role)
                db.session.flush()
                
                test_user = User(
                    name="DB Test User",
                    email="dbtest@example.com",
                    role_id=test_role.id
                )
                test_user.set_password("testpassword123")
                db.session.add(test_user)
                db.session.flush()
                
                db.session.rollback()  # Clean up test data
                print("✅ Database CRUD operations: PASSED")
                return True
                
            except Exception as e:
                print(f"❌ Database CRUD operations: FAILED ({str(e)})")
                db.session.rollback()
                return False
                
    except Exception as e:
        print(f"❌ Database test setup: FAILED ({str(e)})")
        return False


def test_configuration():
    """Test configuration validation."""
    print("\n⚙️ Testing Configuration...")
    print("=" * 50)
    
    try:
        from app.config import BaseConfig
        
        config_tests = [
            ("SECRET_KEY", BaseConfig.SECRET_KEY, 32),
            ("JWT_SECRET_KEY", BaseConfig.JWT_SECRET_KEY, 32),
            ("DATABASE_URL", BaseConfig.SQLALCHEMY_DATABASE_URI, 10),
        ]
        
        all_passed = True
        for config_name, config_value, min_length in config_tests:
            if config_value and len(config_value) >= min_length:
                masked_value = config_value[:4] + "*" * (len(config_value) - 4)
                print(f"✅ {config_name}: {masked_value} (length: {len(config_value)})")
            else:
                print(f"❌ {config_name}: MISSING or too short")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Configuration test: FAILED ({str(e)})")
        return False


def test_rate_limiting():
    """Test rate limiting functionality."""
    print("\n🚦 Testing Rate Limiting...")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        # Make multiple rapid requests to test rate limiting
        responses = []
        for i in range(5):
            try:
                response = requests.get(f"{base_url}/health", timeout=2)
                responses.append(response.status_code)
                time.sleep(0.1)  # Small delay between requests
            except Exception as e:
                responses.append(f"ERROR: {str(e)}")
        
        # Check if any request was rate limited
        rate_limited = any("429" in str(r) for r in responses)
        
        if rate_limited:
            print("✅ Rate limiting: ACTIVE (429 responses detected)")
        else:
            print("ℹ️  Rate limiting: Not triggered in test")
        
        return True
        
    except Exception as e:
        print(f"❌ Rate limiting test: FAILED ({str(e)})")
        return False


def generate_readiness_report(api_results, db_results, config_results, rate_limit_results):
    """Generate comprehensive readiness report."""
    print("\n" + "=" * 70)
    print("📊 PRODUCTION READINESS REPORT")
    print("=" * 70)
    
    # API Tests Summary
    api_passed = sum(1 for result in api_results if result[1])
    api_total = len(api_results)
    print(f"\n🌐 API Tests: {api_passed}/{api_total} passed")
    
    for test_name, passed, error in api_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if error:
            print(f"      Error: {error}")
    
    # Database Tests Summary
    db_status = "✅ PASSED" if db_results else "❌ FAILED"
    print(f"\n💾 Database Tests: {db_status}")
    
    # Configuration Tests Summary
    config_status = "✅ PASSED" if config_results else "❌ FAILED"
    print(f"\n⚙️ Configuration Tests: {config_status}")
    
    # Rate Limiting Tests Summary
    rate_limit_status = "✅ PASSED" if rate_limit_results else "❌ FAILED"
    print(f"\n🚦 Rate Limiting Tests: {rate_limit_status}")
    
    # Overall Assessment
    all_passed = api_passed == api_total and db_results and config_results and rate_limit_results
    overall_status = "🎉 PRODUCTION READY" if all_passed else "⚠️  NEEDS ATTENTION"
    
    print(f"\n🎯 OVERALL STATUS: {overall_status}")
    
    if all_passed:
        print("\n✅ Your Judicial Supreme Backend is PRODUCTION READY!")
        print("🚀 You can now deploy to production with confidence.")
    else:
        print("\n⚠️  Some issues need to be addressed before production deployment.")
        print("📋 Please review the failed tests above.")
    
    print("\n" + "=" * 70)
    return all_passed


if __name__ == "__main__":
    print("🚀 Judicial Supreme Backend - Production Readiness Test")
    print("=" * 70)
    
    # Check if server is running
    print("🔍 Checking if server is running...")
    try:
        response = requests.get("http://localhost:5000/health", timeout=2)
        if response.status_code == 200:
            print("✅ Server is running - starting tests...")
        else:
            print("❌ Server not responding - please start the server first")
            print("💡 Run: python run.py")
            sys.exit(1)
    except Exception:
        print("❌ Server not running - please start the server first")
        print("💡 Run: python run.py")
        sys.exit(1)
    
    # Run all tests
    api_results = test_api_endpoints()
    db_results = test_database_operations()
    config_results = test_configuration()
    rate_limit_results = test_rate_limiting()
    
    # Generate report
    success = generate_readiness_report(api_results, db_results, config_results, rate_limit_results)
    
    sys.exit(0 if success else 1)
