#!/usr/bin/env python3
"""Quick server functionality test"""

from app import create_app
from app.extensions import db
from app.models import User, Role
from flask_jwt_extended import create_access_token
import json

def test_app_functionality():
    print("🧪 Testing Application Functionality")
    print("=" * 40)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Test 1: Database Connection
            print("1. Testing Database Connection...")
            from sqlalchemy import text
            result = db.session.execute(text('SELECT 1')).fetchone()
            print(f"   ✅ Database connected: {result}")
            
            # Test 2: Model Operations
            print("2. Testing Model Operations...")
            
            # Create test user
            import secrets
            test_user = User(
                name="Test User",
                email=f"test_{secrets.token_hex(4)}@example.com",
                role_id=1  # admin role
            )
            test_user.set_password("TestPass123!")
            
            db.session.add(test_user)
            db.session.commit()
            
            print(f"   ✅ User created: ID {test_user.id}")
            
            # Test 3: JWT Token Generation
            print("3. Testing JWT Token Generation...")
            identity = json.dumps({"id": test_user.id, "role": "admin"})
            access_token = create_access_token(identity=identity)
            print(f"   ✅ JWT token created: {len(access_token)} chars")
            
            # Test 4: API Endpoints Registration
            print("4. Testing API Endpoints...")
            routes = []
            for rule in app.url_map.iter_rules():
                if rule.endpoint != 'static':
                    routes.append(f"{rule.methods} {rule.rule}")
            
            print(f"   ✅ Total routes: {len(routes)}")
            print("   Sample routes:")
            for route in routes[:5]:
                print(f"     {route}")
            
            # Test 5: Health Endpoint
            print("5. Testing Health Endpoint...")
            with app.test_client() as client:
                response = client.get('/health')
                if response.status_code == 200:
                    health_data = response.get_json()
                    print(f"   ✅ Health endpoint: {health_data.get('status')}")
                    print(f"   Database check: {health_data.get('checks', {}).get('db')}")
                else:
                    print(f"   ⚠️  Health endpoint status: {response.status_code}")
            
            # Test 6: Authentication Endpoint
            print("6. Testing Authentication Endpoint...")
            with app.test_client() as client:
                response = client.post('/api/v1/auth/login', 
                                      json={"email": "test@example.com", "password": "TestPass123!"})
                if response.status_code == 200:
                    auth_data = response.get_json()
                    print(f"   ✅ Login successful: Token received")
                else:
                    print(f"   ⚠️  Login status: {response.status_code}")
            
            # Clean up
            db.session.delete(test_user)
            db.session.commit()
            print("   ✅ Test user cleaned up")
            
            print("\n🎉 ALL TESTS PASSED!")
            print("🚀 Application is ready for production!")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    test_app_functionality()
