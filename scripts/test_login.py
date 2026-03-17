#!/usr/bin/env python3
"""
Test login functionality with correct credentials.
"""

import os
import sys
import json

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

def test_login():
    """Test login with correct credentials."""
    
    app = create_app()
    
    with app.test_client() as client:
        print("🔑 Testing Login Functionality")
        print("=" * 40)
        
        # Test with correct credentials
        response = client.post('/api/v1/auth/login',
                              json={'email': 'lawyer@judicial.com', 'password': 'Lawyer123!'},
                              content_type='application/json')
        
        print(f"📝 Login attempt (lawyer@judicial.com): {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            print("✅ Login successful!")
            print(f"🎫 Access Token: {data['data']['access_token'][:50]}...")
            print(f"👤 User Info: {data['data']['user']['name']} ({data['data']['user']['role']})")
            
            # Test protected endpoint with token
            token = data['data']['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            
            case_response = client.get('/api/v1/case', headers=headers)
            print(f"📋 Protected endpoint test: {case_response.status_code}")
            
            if case_response.status_code == 200:
                case_data = case_response.get_json()
                print(f"✅ Protected endpoint accessible! Found {case_data['data']['pagination']['total']} cases")
            else:
                print(f"❌ Protected endpoint failed: {case_response.get_json()}")
                
        else:
            print(f"❌ Login failed: {response.get_json()}")
        
        # Test other users
        users = [
            ('admin@judicial.com', 'Admin123!'),
            ('judge@judicial.com', 'Judge123!'),
            ('citizen@judicial.com', 'Citizen123!')
        ]
        
        print("\n👥 Testing Other Users:")
        for email, password in users:
            response = client.post('/api/v1/auth/login',
                                  json={'email': email, 'password': password},
                                  content_type='application/json')
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ {email}: {data['data']['user']['role']}")
            else:
                print(f"❌ {email}: Failed")

if __name__ == "__main__":
    test_login()
