#!/usr/bin/env python3
"""
Test signup with truly unique user
"""

import requests
import json
import uuid

def test_truly_unique_signup():
    """Test signup with truly unique user"""
    base_url = "http://localhost:5000"
    
    print("🧪 Truly Unique User Sign Up Test")
    print("=" * 50)
    
    # Generate truly unique user
    unique_id = str(uuid.uuid4())[:8]
    signup_data = {
        "name": f"Unique User {unique_id}",
        "email": f"unique{unique_id}@test.com",
        "password": "password123",
        "role": "lawyer"
    }
    
    print(f"📧 Testing with unique email: {signup_data['email']}")
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/signup",
            json=signup_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Body: {response.text}")
        
        if response.status_code == 201:
            print("🎉 SIGNUP SUCCESS!")
            data = response.json()
            print(f"🎉 User Data: {data.get('data', {})}")
            print(f"🔑 Access Token: {data.get('data', {}).get('access_token', 'N/A')[:50]}...")
        else:
            print("❌ SIGNUP FAILED")
            
    except Exception as e:
        print(f"❌ Request Error: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
    
    print("\n" + "=" * 50)
    print("🏁 Test Complete!")

if __name__ == "__main__":
    test_truly_unique_signup()
