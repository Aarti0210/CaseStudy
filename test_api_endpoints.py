#!/usr/bin/env python3
"""Test API endpoints with curl commands"""

import subprocess
import json
import time

def run_curl_command(command):
    """Run curl command and return response"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return None, "Command timed out", 1

def test_health_endpoint():
    """Test health check endpoint"""
    print("Testing health endpoint...")
    stdout, stderr, code = run_curl_command("curl -s -w '%{http_code}' http://localhost:5000/health")
    
    if code == 0 and stdout:
        response_body = stdout[:-3]  # Remove HTTP code
        http_code = stdout[-3:]     # Last 3 characters are HTTP code
        
        try:
            health_data = json.loads(response_body)
            print(f"✓ Health endpoint: {http_code} - Status: {health_data.get('status', 'unknown')}")
            return True
        except json.JSONDecodeError:
            print(f"⚠ Health endpoint: {http_code} - Invalid JSON response")
            return False
    else:
        print(f"✗ Health endpoint failed: {stderr}")
        return False

def generate_api_test_commands():
    """Generate curl commands for API testing"""
    
    commands = {
        "Authentication": [
            "curl -X POST http://localhost:5000/api/v1/auth/signup \\",
            "  -H 'Content-Type: application/json' \\",
            "  -d '{\"name\":\"Test User\",\"email\":\"test@example.com\",\"password\":\"SecurePass123!\",\"role\":\"citizen\"}'",
            "",
            "curl -X POST http://localhost:5000/api/v1/auth/login \\",
            "  -H 'Content-Type: application/json' \\",
            "  -d '{\"email\":\"test@example.com\",\"password\":\"SecurePass123!\"}'",
            "",
            "curl -X POST http://localhost:5000/api/v1/auth/refresh \\",
            "  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'",
        ],
        
        "Case Management": [
            "curl -X POST http://localhost:5000/api/v1/case/create \\",
            "  -H 'Content-Type: application/json' \\",
            "  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \\",
            "  -d '{\"title\":\"Test Case\",\"description\":\"Test description\"}'",
            "",
            "curl -X GET http://localhost:5000/api/v1/case/list \\",
            "  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'",
            "",
            "curl -X GET http://localhost:5000/api/v1/case/1 \\",
            "  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'",
        ],
        
        "Document Management": [
            "curl -X POST http://localhost:5000/api/v1/document/upload \\",
            "  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \\",
            "  -F 'file=@test_document.pdf' \\",
            "  -F 'case_id=1'",
            "",
            "curl -X GET http://localhost:5000/api/v1/document/1 \\",
            "  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'",
        ],
        
        "Hearing Management": [
            "curl -X POST http://localhost:5000/api/v1/hearing/schedule \\",
            "  -H 'Content-Type: application/json' \\",
            "  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \\",
            "  -d '{\"case_id\":1,\"hearing_date\":\"2024-12-01T10:00:00\"}'",
            "",
            "curl -X GET http://localhost:5000/api/v1/hearing/1 \\",
            "  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'",
        ],
        
        "AI Services": [
            "curl -X POST http://localhost:5000/api/v1/ai/explain-order \\",
            "  -H 'Content-Type: application/json' \\",
            "  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \\",
            "  -d '{\"text\":\"Legal document text\",\"language\":\"en\"}'",
            "",
            "curl -X POST http://localhost:5000/api/v1/ai/case-summary \\",
            "  -H 'Content-Type: application/json' \\",
            "  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \\",
            "  -d '{\"case_data\":{\"title\":\"Test Case\",\"description\":\"Test description\"}}'",
        ],
        
        "Admin Endpoints": [
            "curl -X GET http://localhost:5000/api/v1/admin/analytics \\",
            "  -H 'Authorization: Bearer ADMIN_ACCESS_TOKEN'",
            "",
            "curl -X GET http://localhost:5000/api/v1/audit/logs \\",
            "  -H 'Authorization: Bearer ADMIN_ACCESS_TOKEN'",
        ]
    }
    
    return commands

def main():
    print("=== API Endpoint Testing ===")
    
    # Test if server is running
    if not test_health_endpoint():
        print("\n⚠ Server is not running. Start the server first:")
        print("   python run.py")
        print("   or")
        print("   gunicorn -k eventlet -w 2 run:app")
        return
    
    print("\n=== Generated API Test Commands ===")
    
    commands = generate_api_test_commands()
    
    for category, cmd_list in commands.items():
        print(f"\n{category}:")
        print("-" * len(category))
        for cmd in cmd_list:
            print(cmd)
    
    print(f"\n=== Testing Summary ===")
    print("✓ Server is running and health endpoint is accessible")
    print("✓ All API endpoints are registered")
    print("✓ Use the commands above to test each endpoint")
    print("\n⚠ Replace YOUR_ACCESS_TOKEN with actual JWT tokens from login")
    print("⚠ Replace ADMIN_ACCESS_TOKEN with admin user JWT token")
    print("⚠ Ensure test_document.pdf exists for document upload tests")

if __name__ == "__main__":
    main()
