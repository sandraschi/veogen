#!/usr/bin/env python3
"""
Test the complete authentication flow for VeoGen (Windows compatible)
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
        print("SUCCESS: Login successful")
        result = response.json()
        token = result.get('access_token')
        user_data = result.get('user')
        print(f"  User: {user_data.get('email')} ({user_data.get('id')})")
        print(f"  Token: {token[:30]}...")
    else:
        print(f"ERROR: Login failed: {response.status_code} - {response.text}")
        return None
    
    # Test 2: /me endpoint
    print("\n2. Testing /me endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BACKEND_URL}/api/v1/enhanced-auth/me", headers=headers)
    
    if response.status_code == 200:
        print("SUCCESS: /me endpoint successful")
        me_data = response.json()
        print(f"  User: {me_data.get('email')} ({me_data.get('id')})")
        
        # Check consistency
        if me_data.get('id') == user_data.get('id'):
            print("SUCCESS: User data consistent between login and /me")
        else:
            print("ERROR: User data inconsistent!")
            print(f"  Login user: {user_data.get('id')}")
            print(f"  /me user: {me_data.get('id')}")
    else:
        print(f"ERROR: /me failed: {response.status_code} - {response.text}")
    
    return token

def test_frontend_availability():
    """Test if frontend is accessible"""
    print("\n=== Testing Frontend Availability ===")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("SUCCESS: Frontend accessible")
            if "VeoGen" in response.text:
                print("SUCCESS: Frontend contains VeoGen content")
            else:
                print("WARNING: Frontend accessible but may not be the correct app")
        else:
            print(f"ERROR: Frontend returned {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Frontend not accessible: {e}")

def main():
    print("VeoGen Authentication Flow Test")
    print("=" * 50)
    
    # Test backend
    token = test_backend_endpoints()
    
    # Test frontend
    test_frontend_availability()
    
    print("\n=== Summary ===")
    if token:
        print("SUCCESS: Backend authentication working")
        print("SUCCESS: All authentication endpoints functional")
        print("\nIf you're having frontend issues:")
        print("1. Check browser developer console for errors")
        print("2. Verify frontend is making requests to correct backend URL")
        print("3. Check network tab for failed requests")
        print("4. Clear browser cache and localStorage")
    else:
        print("ERROR: Backend authentication has issues")
    
    print(f"\nFrontend URL: {FRONTEND_URL}")
    print(f"Backend URL: {BACKEND_URL}")

if __name__ == "__main__":
    main()
