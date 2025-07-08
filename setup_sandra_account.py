#!/usr/bin/env python3
"""
Create Sandra's user account and test complete email workflow
"""
import requests
import time
import json

def setup_sandra_account():
    print("=== Setting Up Sandra's VeoGen Account ===")
    
    # Your account details
    sandra_user = {
        'email': 'sandraschipal@hotmail.com',
        'password': 'S3c1000vg#',
        'username': 'sas13',
        'full_name': 'Sandra Schipal'
    }
    
    print("1. Creating your account...")
    try:
        response = requests.post('http://localhost:4700/api/v1/enhanced-auth/register', 
                               json=sandra_user)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("   SUCCESS: Account created!")
            print(f"   User: {data.get('user', {}).get('email', 'unknown')}")
            token = data.get('access_token', '')
            print(f"   Token: {token[:20] if token else 'none'}...")
            
            # Save token for further testing
            with open('sandra_token.txt', 'w') as f:
                f.write(token)
            
        elif response.status_code == 400:
            print("   INFO: Account might already exist, trying login...")
            # Try login instead
            login_response = requests.post('http://localhost:4700/api/v1/enhanced-auth/login', 
                                         json={'email': sandra_user['email'], 'password': sandra_user['password']})
            if login_response.status_code == 200:
                print("   SUCCESS: Logged in with existing account!")
                data = login_response.json()
                token = data.get('access_token', '')
                with open('sandra_token.txt', 'w') as f:
                    f.write(token)
            else:
                print(f"   Login failed: {login_response.text}")
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    print("\n2. Testing password reset for your account...")
    try:
        response = requests.post('http://localhost:4700/api/v1/enhanced-auth/request-password-reset', 
                               json={'email': 'sandraschipal@hotmail.com'})
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   SUCCESS: Password reset email triggered!")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n3. Testing email verification resend...")
    try:
        # Load token if available
        token = ""
        try:
            with open('sandra_token.txt', 'r') as f:
                token = f.read().strip()
        except:
            pass
            
        if token:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.post('http://localhost:4700/api/v1/enhanced-auth/resend-verification', 
                                   headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   SUCCESS: Verification email triggered!")
            else:
                print(f"   Error: {response.text}")
        else:
            print("   SKIP: No token available for verification resend")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    return True

if __name__ == "__main__":
    setup_sandra_account()
