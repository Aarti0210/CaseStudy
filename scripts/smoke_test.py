#!/usr/bin/env python3
"""
Smoke test script for Render deployment verification.
Tests all critical endpoints to ensure deployment is successful.
"""

import requests
import json
import time
import sys
from typing import Dict, Any

class RenderSmokeTest:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.results = []
        
    def log_test(self, test_name: str, success: bool, message: str = "", response_data: Any = None):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"    {message}")
        if response_data:
            print(f"    Response: {json.dumps(response_data, indent=2)[:200]}...")
        
        self.results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': time.time()
        })
    
    def test_health_endpoint(self):
        """Test the health check endpoint."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'ok' and data.get('service') == 'judicial-backend':
                    self.log_test("Health Check", True, "Service is healthy", data)
                    return True
                else:
                    self.log_test("Health Check", False, f"Invalid response: {data}")
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {e}")
        return False
    
    def test_api_docs(self):
        """Test the API documentation endpoint."""
        try:
            response = requests.get(f"{self.base_url}/api/v1/docs/openapi.json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('info') and data.get('openapi'):
                    self.log_test("API Documentation", True, "OpenAPI spec available")
                    return True
                else:
                    self.log_test("API Documentation", False, "Invalid OpenAPI spec")
            else:
                self.log_test("API Documentation", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("API Documentation", False, f"Connection error: {e}")
        return False
    
    def test_auth_endpoint(self):
        """Test authentication endpoint."""
        try:
            # Test login with invalid credentials (should return 401)
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"email": "test@example.com", "password": "wrongpassword"},
                timeout=10
            )
            if response.status_code in [400, 401]:
                self.log_test("Auth Endpoint", True, "Login endpoint responding correctly")
                return True
            elif response.status_code == 200:
                self.log_test("Auth Endpoint", False, "Login should fail with wrong credentials")
            else:
                self.log_test("Auth Endpoint", False, f"Unexpected HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Auth Endpoint", False, f"Connection error: {e}")
        return False
    
    def test_case_endpoint(self):
        """Test case endpoint (should require authentication)."""
        try:
            response = requests.get(f"{self.base_url}/api/v1/case", timeout=10)
            if response.status_code == 401:
                self.log_test("Case Endpoint", True, "Properly requires authentication")
                return True
            else:
                self.log_test("Case Endpoint", False, f"Should require auth, got HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Case Endpoint", False, f"Connection error: {e}")
        return False
    
    def test_ai_endpoint(self):
        """Test AI endpoint (should require authentication)."""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/ai/case-summary",
                json={"case_data": "test case"},
                timeout=10
            )
            if response.status_code == 401:
                self.log_test("AI Endpoint", True, "Properly requires authentication")
                return True
            else:
                self.log_test("AI Endpoint", False, f"Should require auth, got HTTP {response.status_code}")
        except Exception as e:
            self.log_test("AI Endpoint", False, f"Connection error: {e}")
        return False
    
    def test_cors_headers(self):
        """Test CORS headers are properly set."""
        try:
            response = requests.options(f"{self.base_url}/api/v1/case", timeout=10)
            cors_headers = {
                'Access-Control-Allow-Origin',
                'Access-Control-Allow-Methods',
                'Access-Control-Allow-Headers'
            }
            
            has_cors = any(header in response.headers for header in cors_headers)
            if has_cors:
                self.log_test("CORS Headers", True, "CORS properly configured")
                return True
            else:
                self.log_test("CORS Headers", False, "CORS headers missing")
        except Exception as e:
            self.log_test("CORS Headers", False, f"Connection error: {e}")
        return False
    
    def test_websocket_upgrade(self):
        """Test WebSocket upgrade headers."""
        try:
            headers = {
                'Upgrade': 'websocket',
                'Connection': 'Upgrade',
                'Sec-WebSocket-Key': 'test',
                'Sec-WebSocket-Version': '13'
            }
            response = requests.get(
                f"{self.base_url}/socket.io/",
                headers=headers,
                timeout=5
            )
            # Should either upgrade or return proper WebSocket response
            if response.status_code in [200, 400, 101]:
                self.log_test("WebSocket Support", True, "WebSocket endpoint responding")
                return True
            else:
                self.log_test("WebSocket Support", False, f"WebSocket not responding, HTTP {response.status_code}")
        except Exception as e:
            self.log_test("WebSocket Support", False, f"Connection error: {e}")
        return False
    
    def run_all_tests(self):
        """Run all smoke tests."""
        print(f"🚀 Running smoke tests for: {self.base_url}")
        print("=" * 60)
        
        tests = [
            self.test_health_endpoint,
            self.test_api_docs,
            self.test_auth_endpoint,
            self.test_case_endpoint,
            self.test_ai_endpoint,
            self.test_cors_headers,
            self.test_websocket_upgrade
        ]
        
        for test in tests:
            test()
            time.sleep(1)  # Brief pause between tests
        
        print("=" * 60)
        
        # Summary
        passed = sum(1 for r in self.results if r['success'])
        total = len(self.results)
        
        print(f"📊 Test Results: {passed}/{total} passed")
        
        if passed == total:
            print("🎉 All tests passed! Backend is ready for production.")
            return True
        else:
            print("⚠️  Some tests failed. Check the deployment configuration.")
            return False

def main():
    """Main smoke test function."""
    if len(sys.argv) != 2:
        print("Usage: python smoke_test.py <base_url>")
        print("Example: python smoke_test.py https://judicial-supreme-backend.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1]
    smoke_test = RenderSmokeTest(base_url)
    success = smoke_test.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
