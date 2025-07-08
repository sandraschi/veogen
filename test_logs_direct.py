#!/usr/bin/env python3
"""
Direct test of logs endpoint
"""

import requests
import json
import sys

def test_logs_endpoint():
    """Test the logs endpoint directly"""
    print("Testing logs endpoint directly...")
    
    try:
        # Get auth token first
        auth_response = requests.post(
            "http://localhost:4700/api/v1/auth/login",
            json={
                "email": "valid@test.com", 
                "password": "Test123!"
            }
        )
        
        if auth_response.status_code != 200:
            print(f"Auth failed: {auth_response.status_code}")
            print(f"Response: {auth_response.text}")
            return False
            
        token = auth_response.json().get("access_token")
        print(f"Got auth token: {token[:20]}...")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test logs endpoint
        logs_url = "http://localhost:4700/api/v1/logs/"
        print(f"Testing: {logs_url}")
        
        logs_response = requests.get(logs_url, headers=headers)
        
        print(f"Status: {logs_response.status_code}")
        print(f"Headers: {dict(logs_response.headers)}")
        
        if logs_response.status_code == 200:
            data = logs_response.json()
            print(f"SUCCESS! Got {len(data.get('logs', []))} logs")
            print(f"Available components: {data.get('available_components', [])}")
            print(f"Available levels: {data.get('available_levels', [])}")
            return True
        else:
            print(f"FAILED: {logs_response.status_code}")
            print(f"Response: {logs_response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_logs_endpoint()
    sys.exit(0 if success else 1)
