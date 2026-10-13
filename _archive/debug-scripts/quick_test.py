#!/usr/bin/env python3
"""
Quick test for the logs API endpoint
"""

import requests
import json

def test_logs_endpoint():
    """Test the logs endpoint directly"""
    print("Testing logs endpoint...")
    
    try:
        # First authenticate
        auth_response = requests.post(
            "http://localhost:4700/api/v1/auth/login",
            json={
                "email": "valid@test.com",
                "password": "Test123!"
            }
        )
        
        print(f"Auth response: {auth_response.status_code}")
        if auth_response.status_code == 200:
            token = auth_response.json().get("access_token")
            print(f"Token received: {token[:20]}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test logs endpoint
            logs_response = requests.get(
                "http://localhost:4700/api/v1/logs/",
                headers=headers
            )
            
            print(f"Logs response: {logs_response.status_code}")
            if logs_response.status_code == 200:
                data = logs_response.json()
                print(f"Success! Logs: {len(data.get('logs', []))}")
                print(f"Components: {data.get('available_components', [])}")
                return True
            else:
                print(f"Logs failed: {logs_response.text}")
                return False
        else:
            print(f"Auth failed: {auth_response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_docsify():
    """Test docsify endpoint"""
    print("\nTesting docsify...")
    
    try:
        response = requests.get("http://localhost:4700/docs/")
        print(f"Docsify response: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            print(f"Content length: {len(content)}")
            print(f"Contains 'docsify': {'docsify' in content.lower()}")
            print(f"Contains 'veogen': {'veogen' in content.lower()}")
            print(f"First 200 chars: {content[:200]}")
            return True
        else:
            print(f"Failed: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_logs_endpoint()
    test_docsify()
