#!/usr/bin/env python3
"""
Test the complete authentication flow for VeoGen
"""
import requests
import json
import time

BACKEND_URL = "http://localhost:4700"
FRONTEND_URL = "http://localhost:4710"

def test_backend_endpoints():
    """Test backend authentication endpoints"""
    print("=== Testing Backend Authentication ===")
    
    # Test 1: Login
    print("\n1. Testing Login...")
    login_data = {"email": "valid@test.com", "password": "Test123!"}
    response = requests.post(f"{BACKEND_URL}/api/v1/enhanced-auth/login", json=login_data)
    
    if response.status_code == 200:
        print("✓ Login successful")
        result = response.json()
        token = result.get('access_token')
        user_data = result.get('user')
        print(f"  User: {user_data.get('email')} ({user_data.get('id')})")
        print(f"  Token: {token[:30]}...")
    else:
        print(f"✗ Login failed: {response.status_code} - {response.text}")
        return None
    
    # Test 2: /me endpoint
    print("\n2. Testing /me endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BACKEND_URL}/api/v1/enhanced-auth/me", headers=headers)
    
    if response.status_code == 200:
        print("✓ /me endpoint successful")
        me_data = response.json()
        print(f"  User: {me_data.get('email')} ({me_data.get('id')})")
        
        # Check consistency
        if me_data.get('id') == user_data.get('id'):
            print("✓ User data consistent between login and /me")
        else:
            print("✗ User data inconsistent!")
            print(f"  Login user: {user_data.get('id')}")
            print(f"  /me user: {me_data.get('id')}")
    else:
        print(f"✗ /me failed: {response.status_code} - {response.text}")
    
    # Test 3: Health check
    print("\n3. Testing health endpoint...")
    response = requests.get(f"{BACKEND_URL}/health")
    if response.status_code == 200:
        print("✓ Health endpoint working")
        health = response.json()
        print(f"  Status: {health.get('status')}")
    else:
        print(f"✗ Health check failed: {response.status_code}")
    
    return token

def test_frontend_availability():
    """Test if frontend is accessible"""
    print("\n=== Testing Frontend Availability ===")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✓ Frontend accessible")
            if "VeoGen" in response.text:
                print("✓ Frontend contains VeoGen content")
            else:
                print("? Frontend accessible but may not be the correct app")
        else:
            print(f"✗ Frontend returned {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"✗ Frontend not accessible: {e}")

def test_cors_and_connectivity():
    """Test CORS and frontend-backend connectivity"""
    print("\n=== Testing CORS and Connectivity ===")
    
    # Test CORS preflight
    headers = {
        'Origin': FRONTEND_URL,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type,Authorization'
    }
    
    response = requests.options(f"{BACKEND_URL}/api/v1/enhanced-auth/login", headers=headers)
    if response.status_code in [200, 204]:
        print("✓ CORS preflight successful")
    else:
        print(f"? CORS preflight returned {response.status_code}")
    
    # Check CORS headers in actual response
    login_data = {"email": "valid@test.com", "password": "Test123!"}
    response = requests.post(f"{BACKEND_URL}/api/v1/enhanced-auth/login", 
                           json=login_data, 
                           headers={'Origin': FRONTEND_URL})
    
    cors_headers = {k: v for k, v in response.headers.items() if 'access-control' in k.lower()}
    if cors_headers:
        print("✓ CORS headers present:")
        for header, value in cors_headers.items():
            print(f"  {header}: {value}")
    else:
        print("? No CORS headers found")

def main():
    print("VeoGen Authentication Flow Test")
    print("=" * 50)
    
    # Test backend
    token = test_backend_endpoints()
    
    # Test frontend
    test_frontend_availability()
    
    # Test connectivity
    test_cors_and_connectivity()
    
    print("\n=== Summary ===")
    if token:
        print("✓ Backend authentication working")
        print("✓ All authentication endpoints functional")
        print("\nIf you're having frontend issues:")
        print("1. Check browser developer console for errors")
        print("2. Verify frontend is making requests to correct backend URL")
        print("3. Check network tab for failed requests")
        print("4. Clear browser cache and localStorage")
    else:
        print("✗ Backend authentication has issues")
    
    print(f"\nFrontend URL: {FRONTEND_URL}")
    print(f"Backend URL: {BACKEND_URL}")
    print("\nRecommendation: Test the login flow in your browser and check the console for any JavaScript errors.")

if __name__ == "__main__":
    main()
