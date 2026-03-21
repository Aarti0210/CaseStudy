#!/usr/bin/env python3
"""
Direct test of signup endpoint with detailed logging
"""

import requests
import json

def test_signup_direct():
    """Test signup endpoint directly"""
    base_url = "http://localhost:5000"
    
    print("🧪 Direct Signup Test")
    print("=" * 50)
    
    # Test data
    signup_data = {
        "name": "Direct Test User",
        "email": "directtest@example.com",
        "password": "password123",
        "role": "lawyer"
    }
    
    print(f"📤 Sending data: {json.dumps(signup_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/signup",
            json=signup_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        print(f"📊 Response Body: {response.text}")
        
        if response.status_code == 201:
            print("🎉 SIGNUP SUCCESS!")
        else:
            print("❌ SIGNUP FAILED")
            
    except Exception as e:
        print(f"❌ Request Error: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
    
    print("\n" + "=" * 50)
    print("🏁 Test Complete!")

if __name__ == "__main__":
    test_signup_direct()
