#!/usr/bin/env python3
"""
Test backend with new user for signup
"""

import requests
import json

def test_new_user_signup():
    """Test backend with new user"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing New User Sign Up")
    print("=" * 50)
    
    # Test with new user
    signup_data = {
        "name": "New Test User",
        "email": "newuser@example.com",
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
    
    print("\n" + "=" * 50)
    print("🏁 Testing Complete!")

if __name__ == "__main__":
    test_new_user_signup()
