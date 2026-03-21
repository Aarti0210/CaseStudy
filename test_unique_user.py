#!/usr/bin/env python3
"""
Test backend with unique user for signup
"""

import requests
import json
import random

def test_unique_user_signup():
    """Test backend with unique user"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Unique User Sign Up")
    print("=" * 50)
    
    # Generate unique user
    random_id = random.randint(1000, 9999)
    signup_data = {
        "name": f"Test User {random_id}",
        "email": f"testuser{random_id}@example.com",
        "password": "password123",
        "role": "lawyer"
    }
    
    print(f"📧 Testing with email: {signup_data['email']}")
    
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
    
    print("\n" + "=" * 50)
    print("🏁 Testing Complete!")

if __name__ == "__main__":
    test_unique_user_signup()
