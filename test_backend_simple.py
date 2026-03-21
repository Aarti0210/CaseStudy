#!/usr/bin/env python3
"""
Simple test script to verify backend functionality
"""

import requests
import json

def test_backend():
    """Test backend endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Backend Functionality")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n🔍 Test 1: Health Check")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health Status: {response.status_code}")
        if response.status_code == 200:
            print(f"📊 Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.text}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Sign Up
    print("\n👤 Test 2: Sign Up")
    signup_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "role": "lawyer"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/signup",
            json=signup_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"✅ Sign Up Status: {response.status_code}")
        if response.status_code == 201:
            print(f"🎉 Sign Up Success: {response.json()}")
        else:
            print(f"❌ Sign Up Failed: {response.text}")
    except Exception as e:
        print(f"❌ Sign Up Error: {e}")
    
    # Test 3: Login
    print("\n🔐 Test 3: Login")
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"✅ Login Status: {response.status_code}")
        if response.status_code == 200:
            print(f"🎉 Login Success: {response.json()}")
        else:
            print(f"❌ Login Failed: {response.text}")
    except Exception as e:
        print(f"❌ Login Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Testing Complete!")

if __name__ == "__main__":
    test_backend()
