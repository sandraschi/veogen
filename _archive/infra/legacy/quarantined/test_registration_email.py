#!/usr/bin/env python3
"""
Test user registration and email verification
"""
import requests

def test_registration():
    print("=== Testing User Registration with Email ===")
    
    # Test registration
    new_user = {
        'email': 'newregistered@example.com',
        'password': 'NewPass123!',
        'username': 'newregistered', 
        'full_name': 'New Registered User'
    }
    
    print("Testing user registration...")
    try:
        response = requests.post('http://localhost:4700/api/v1/enhanced-auth/register', 
                               json=new_user)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: User registration completed!")
            user_email = data.get("user", {}).get("email", "unknown")
            print(f"User email: {user_email}")
            print(f"Got access token: {bool(data.get('access_token'))}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_registration()
