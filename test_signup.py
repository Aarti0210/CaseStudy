#!/usr/bin/env python3
import requests
import json

def test_signup():
    url = "http://localhost:5000/api/v1/auth/signup"
    
    payload = {
        "name": "John Doe",
        "email": "john@example.com", 
        "password": "SecurePassword123!",
        "role": "citizen"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 500:
            print("\n🔍 500 Error Detected!")
            print("Check the server logs above for detailed error information.")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_signup()
