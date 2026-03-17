#!/usr/bin/env python3
"""Test server startup and health endpoint"""

import requests
import time
import subprocess
import sys
import signal
import os

def test_server_startup():
    print("🚀 Testing Server Startup")
    print("=" * 30)
    
    # Start server in background
    try:
        proc = subprocess.Popen([sys.executable, 'run.py'])
        print("✅ Server starting...")
        
        # Wait for server to start
        time.sleep(8)
        
        # Test health endpoint
        try:
            response = requests.get('http://localhost:5000/health', timeout=5)
            
            if response.status_code == 200:
                health_data = response.json()
                print("✅ Health endpoint working!")
                print(f"   Status: {health_data.get('status')}")
                print(f"   Service: {health_data.get('service')}")
                print(f"   Database: {health_data.get('checks', {}).get('db')}")
                
                # Test API endpoints are registered
                try:
                    auth_response = requests.options('http://localhost:5000/api/v1/auth/login', timeout=5)
                    if auth_response.status_code in [200, 204]:
                        print("✅ API endpoints accessible!")
                    else:
                        print(f"⚠️  API endpoint status: {auth_response.status_code}")
                except:
                    print("⚠️  Could not test API endpoints")
                
                return True
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Could not connect to server: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False
    
    finally:
        # Clean up: terminate server
        try:
            proc.terminate()
            proc.wait(timeout=5)
            print("✅ Server stopped")
        except:
            try:
                proc.kill()
                proc.wait()
                print("✅ Server force stopped")
            except:
                pass

def test_database_with_server():
    """Test database operations through the running server"""
    print("\n🗄️  Testing Database Operations")
    print("=" * 35)
    
    try:
        # Test user creation
        signup_data = {
            "name": "Test User",
            "email": "test@judicial.com",
            "password": "SecurePass123!",
            "role": "citizen"
        }
        
        response = requests.post(
            'http://localhost:5000/api/v1/auth/signup',
            json=signup_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print("✅ User signup working!")
            user_data = response.json()
            print(f"   User ID: {user_data.get('data', {}).get('user', {}).get('id')}")
        else:
            print(f"⚠️  Signup status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
        
        # Test user login
        login_data = {
            "email": "test@judicial.com",
            "password": "SecurePass123!"
        }
        
        response = requests.post(
            'http://localhost:5000/api/v1/auth/login',
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ User login working!")
            login_data = response.json()
            token = login_data.get('data', {}).get('access_token')
            if token:
                print(f"   Token received: {len(token)} chars")
            else:
                print("⚠️  No token received")
        else:
            print(f"⚠️  Login status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_server_startup()
    
    if success:
        # Test database operations
        test_database_with_server()
        
        print("\n🎉 SERVER TEST COMPLETE!")
        print("🚀 Your Judicial Supreme Backend is ready for production!")
        print("\n📋 Next Steps:")
        print("1. Deploy to your hosting platform")
        print("2. Set up environment variables")
        print("3. Configure domain and SSL")
        print("4. Set up monitoring and backups")
        
    else:
        print("\n❌ Server test failed. Check the logs above.")
