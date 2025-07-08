#!/usr/bin/env python3
"""
Test specific endpoint routing
"""
import requests
import json

API_BASE_URL = "http://localhost:4700"

def test_specific_endpoint():
    """Test exactly what the frontend is calling"""
    
    # First, login to get a token
    login_data = {
        "email": "valid@test.com",
        "password": "Test123!"
    }
    
    print("1. Logging in...")
    response = requests.post(f"{API_BASE_URL}/api/v1/enhanced-auth/login", json=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json().get('access_token')
    print(f"   Token: {token[:50]}...")
    
    # Test the exact endpoint the frontend calls
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n2. Testing /api/v1/enhanced-auth/me...")
    response = requests.get(f"{API_BASE_URL}/api/v1/enhanced-auth/me", headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Let's also check if there's another auth endpoint
    print("\n3. Testing /api/v1/auth/me...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/auth/me", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check all available endpoints
    print("\n4. Testing health endpoint (no auth)...")
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    
    print("\n5. Testing docs endpoints...")
    response = requests.get(f"{API_BASE_URL}/docs")
    print(f"   Docs Status: {response.status_code}")

if __name__ == "__main__":
    test_specific_endpoint()
