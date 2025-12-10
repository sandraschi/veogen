#!/usr/bin/env python3
"""
Test the authentication dependency manually inside the container
"""
import requests
import json

API_BASE_URL = "http://localhost:4700"

def test_manual_auth():
    # Get a valid token first
    login_data = {"email": "valid@test.com", "password": "Test123!"}
    response = requests.post(f"{API_BASE_URL}/api/v1/enhanced-auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"Token: {token[:50]}...")
    
    # Test the me endpoint
    response = requests.get(f"{API_BASE_URL}/api/v1/enhanced-auth/me", headers=headers)
    print(f"/me endpoint status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"User returned: {result.get('id')} ({result.get('email')})")
        
        # This should be 'valid_user' not 'admin'
        if result.get('id') == 'valid_user':
            print("SUCCESS: SUCCESS: Correct user returned!")
        else:
            print("ERROR: PROBLEM: Wrong user returned - expected 'valid_user'")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_manual_auth()
