#!/usr/bin/env python3
"""
Create test data for development and testing.
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user import User
from app.models.role import Role
from app.extensions import db

def create_test_data():
    """Create test users and roles."""
    
    app = create_app()
    
    with app.app_context():
        print("🔧 Creating Test Data")
        print("=" * 30)
        
        try:
            # Create roles
            roles = [
                {"name": "admin", "description": "System administrator"},
                {"name": "judge", "description": "Court judge"},
                {"name": "lawyer", "description": "Legal lawyer"},
                {"name": "citizen", "description": "Regular citizen"}
            ]
            
            for role_data in roles:
                role = Role.query.filter_by(name=role_data["name"]).first()
                if not role:
                    role = Role(**role_data)
                    db.session.add(role)
                    print(f"✅ Created role: {role_data['name']}")
                else:
                    print(f"⚠️  Role already exists: {role_data['name']}")
            
            db.session.commit()
            
            # Create test users
            test_users = [
                {
                    "name": "Admin User",
                    "email": "admin@judicial.com",
                    "password": "Admin123!",
                    "role": "admin"
                },
                {
                    "name": "Judge Smith",
                    "email": "judge@judicial.com",
                    "password": "Judge123!",
                    "role": "judge"
                },
                {
                    "name": "Lawyer Johnson",
                    "email": "lawyer@judicial.com",
                    "password": "Lawyer123!",
                    "role": "lawyer"
                },
                {
                    "name": "Citizen Doe",
                    "email": "citizen@judicial.com",
                    "password": "Citizen123!",
                    "role": "citizen"
                }
            ]
            
            for user_data in test_users:
                user = User.query.filter_by(email=user_data["email"]).first()
                if not user:
                    role = Role.query.filter_by(name=user_data["role"]).first()
                    user = User(
                        name=user_data["name"],
                        email=user_data["email"],
                        role_obj=role
                    )
                    user.set_password(user_data["password"])
                    db.session.add(user)
                    print(f"✅ Created user: {user_data['email']} ({user_data['role']})")
                else:
                    print(f"⚠️  User already exists: {user_data['email']}")
            
            db.session.commit()
            
            print("=" * 30)
            print("✅ Test data creation complete!")
            print("\n📋 Test Users Created:")
            for user_data in test_users:
                print(f"  📧 {user_data['email']} / 🔑 {user_data['password']} ({user_data['role']})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating test data: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = create_test_data()
    sys.exit(0 if success else 1)
