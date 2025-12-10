#!/usr/bin/env python3
"""
Test the debug endpoint specifically
"""
import requests

API_BASE_URL = "http://localhost:4700"

def test_debug_auth():
    # Login first
    login_data = {"email": "valid@test.com", "password": "Test123!"}
    response = requests.post(f"{API_BASE_URL}/api/v1/enhanced-auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json().get('access_token')
    print(f"Token: {token[:50]}...")
    
    # Test debug endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE_URL}/api/v1/enhanced-auth/debug-auth", headers=headers)
    
    print(f"Debug Auth Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Debug Response: {response.json()}")
    else:
        print(f"Debug Error: {response.text}")
    
    # Test original /me endpoint
    response = requests.get(f"{API_BASE_URL}/api/v1/enhanced-auth/me", headers=headers)
    print(f"Me Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Me Response User ID: {result.get('id')}")
        print(f"Me Response Email: {result.get('email')}")
    else:
        print(f"Me Error: {response.text}")

if __name__ == "__main__":
    test_debug_auth()
