#!/usr/bin/env python3
"""
Debug script to test login endpoint and identify issues.
"""

import os
import sys
import json

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user import User
from app.models.role import Role
from app.extensions import db

def debug_login():
    """Debug login endpoint issues."""
    
    app = create_app()
    
    with app.app_context():
        print("🔍 Debugging Login Endpoint Issues")
        print("=" * 50)
        
        # Check database connection
        try:
            db.session.execute("SELECT 1")
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
        
        # Check if User table exists
        try:
            User.query.first()
            print("✅ User model accessible")
        except Exception as e:
            print(f"❌ User model error: {e}")
            return False
        
        # Check if Role table exists
        try:
            Role.query.first()
            print("✅ Role model accessible")
        except Exception as e:
            print(f"❌ Role model error: {e}")
            return False
        
        # Check user count
        try:
            user_count = User.query.count()
            print(f"📊 Total users in database: {user_count}")
            
            if user_count == 0:
                print("⚠️  No users found - creating test user...")
                create_test_user()
        except Exception as e:
            print(f"❌ Error counting users: {e}")
        
        # Check role count
        try:
            role_count = Role.query.count()
            print(f"📊 Total roles in database: {role_count}")
            
            if role_count == 0:
                print("⚠️  No roles found - creating default roles...")
                create_default_roles()
        except Exception as e:
            print(f"❌ Error counting roles: {e}")
        
        # Test a sample user
        try:
            test_user = User.query.first()
            if test_user:
                print(f"👤 Sample user found: {test_user.email}")
                print(f"🔑 User has role_obj: {hasattr(test_user, 'role_obj')}")
                if hasattr(test_user, 'role_obj') and test_user.role_obj:
                    print(f"🏷️  User role: {test_user.role_obj.name}")
                else:
                    print("⚠️  User has no role_obj or role is None")
                
                # Test password checking
                if hasattr(test_user, 'check_password'):
                    print("✅ User has check_password method")
                    try:
                        # Test with wrong password
                        result = test_user.check_password("wrong_password")
                        print(f"🔐 Password check (wrong): {result}")
                    except Exception as e:
                        print(f"❌ Password check error: {e}")
                else:
                    print("❌ User missing check_password method")
            else:
                print("⚠️  No users found in database")
        except Exception as e:
            print(f"❌ Error testing sample user: {e}")
        
        print("=" * 50)
        print("🔧 Debug Complete")
        return True

def create_test_user():
    """Create a test user for debugging."""
    try:
        # Ensure lawyer role exists
        lawyer_role = Role.query.filter_by(name="lawyer").first()
        if not lawyer_role:
            lawyer_role = Role(name="lawyer")
            db.session.add(lawyer_role)
        
        # Create test user
        test_user = User(
            name="Test User",
            email="test@judicial.com",
            role_obj=lawyer_role
        )
        test_user.set_password("TestPassword123!")
        
        db.session.add(test_user)
        db.session.commit()
        
        print("✅ Test user created: test@judicial.com / TestPassword123!")
        return True
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        db.session.rollback()
        return False

def create_default_roles():
    """Create default roles."""
    try:
        roles = ["admin", "judge", "lawyer", "citizen"]
        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name)
                db.session.add(role)
        
        db.session.commit()
        print("✅ Default roles created")
        return True
    except Exception as e:
        print(f"❌ Error creating roles: {e}")
        db.session.rollback()
        return False

def test_login_endpoint():
    """Test the login endpoint directly."""
    app = create_app()
    
    with app.test_client() as client:
        print("\n🌐 Testing Login Endpoint")
        print("-" * 30)
        
        # Test with missing credentials
        response = client.post('/api/v1/auth/login', 
                              json={}, 
                              content_type='application/json')
        print(f"📝 Empty login request: {response.status_code}")
        if response.status_code != 200:
            print(f"   Response: {response.get_json()}")
        
        # Test with invalid credentials
        response = client.post('/api/v1/auth/login',
                              json={'email': 'wrong@test.com', 'password': 'wrong'},
                              content_type='application/json')
        print(f"📝 Invalid credentials: {response.status_code}")
        if response.status_code != 200:
            print(f"   Response: {response.get_json()}")
        
        # Test with valid credentials (if test user exists)
        response = client.post('/api/v1/auth/login',
                              json={'email': 'test@judicial.com', 'password': 'TestPassword123!'},
                              content_type='application/json')
        print(f"📝 Valid credentials: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   ✅ Login successful!")
            print(f"   🎫 Access token: {data['data']['access_token'][:50]}...")
        else:
            print(f"   Response: {response.get_json()}")

if __name__ == "__main__":
    debug_login()
    test_login_endpoint()
