#!/usr/bin/env python3
"""
VeoGen Real Email Test - Using sandraschipal@hotmail.com
This will send actual emails to Sandra's real email address for testing
"""

import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:4700"

def test_real_email_flows():
    print("VeoGen Real Email Testing")
    print("Using: sandraschipal@hotmail.com")
    print("=" * 50)
    
    # Test 1: Try to register with Sandra's email (might already exist)
    print("\nTest 1: Registration Test")
    sandra_email = "sandraschipal@hotmail.com"
    
    # Try to register (might fail if already exists)
    register_data = {
        "email": sandra_email,
        "password": "TestEmail123!",
        "username": f"sandra_test_{int(time.time())}",
        "full_name": "Sandra Schipal Test"
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/v1/enhanced-auth/register", json=register_data)
        print(f"Registration Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: New user registered")
            print(f"Email verified: {data['user']['is_verified']}")
            print(f"Verification email sent to: {sandra_email}")
            token = data['access_token']
            user_id = data['user']['id']
        elif response.status_code == 400:
            print(f"INFO: User already exists (expected)")
            print(f"Response: {response.text}")
            # Try to login instead
            login_data = {
                "email": sandra_email,
                "password": "S3c1000vg#"  # Sandra's existing password
            }
            login_response = requests.post(f"{API_BASE}/api/v1/enhanced-auth/login", json=login_data)
            if login_response.status_code == 200:
                login_data = login_response.json()
                print(f"SUCCESS: Logged in with existing account")
                token = login_data['access_token']
                user_id = login_data['user']['id']
                print(f"User ID: {user_id}")
                print(f"Email verified: {login_data['user']['is_verified']}")
            else:
                print(f"FAILED: Could not login: {login_response.text}")
                return
        else:
            print(f"FAILED: Registration failed: {response.text}")
            return
            
    except Exception as e:
        print(f"ERROR: Registration error: {e}")
        return

    # Test 2: Request password reset (this will send real email)
    print("\nTest 2: Password Reset Email")
    try:
        reset_data = {"email": sandra_email}
        response = requests.post(f"{API_BASE}/api/v1/enhanced-auth/request-password-reset", 
                               json=reset_data)
        print(f"Reset Request Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Password reset email sent to {sandra_email}")
            print(f"Message: {data['message']}")
            print(f"CHECK YOUR EMAIL: Look for password reset link")
        else:
            print(f"FAILED: Reset request failed: {response.text}")
            
    except Exception as e:
        print(f"ERROR: Reset request error: {e}")

    # Test 3: Try resend verification (if user is not verified)
    print("\nTest 3: Resend Verification Email")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{API_BASE}/api/v1/enhanced-auth/resend-verification", 
                               headers=headers)
        print(f"Resend Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: {data['message']}")
            print(f"CHECK YOUR EMAIL: Look for verification link")
        elif response.status_code == 404:
            print(f"FAILED: Resend endpoint not found (known issue)")
            print(f"Response: {response.text}")
        else:
            print(f"INFO: {response.text}")
            
    except Exception as e:
        print(f"ERROR: Resend error: {e}")

    # Test 4: Check user info
    print("\nTest 4: Current User Info")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/api/v1/enhanced-auth/me", headers=headers)
        print(f"User Info Status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"Current user: {user_data['email']}")
            print(f"Email verified: {user_data['is_verified']}")
            print(f"Onboarding complete: {user_data.get('onboarding', {}).get('is_complete', 'Unknown')}")
        else:
            print(f"FAILED: Could not get user info: {response.text}")
            
    except Exception as e:
        print(f"ERROR: User info error: {e}")

    print("\n" + "=" * 50)
    print("EMAIL TEST INSTRUCTIONS:")
    print("=" * 50)
    print(f"1. CHECK YOUR EMAIL: {sandra_email}")
    print("2. Look for emails from VeoGen with subject lines like:")
    print("   - 'Verify Your Email Address'")
    print("   - 'Password Reset Request'")
    print("3. Click the verification link if you got one")
    print("4. Try the password reset link if you got one")
    print("5. Report back what you received!")
    
    print("\nIf you don't see emails:")
    print("- Check spam/junk folder")
    print("- Check if email system is configured correctly")
    print("- Check backend logs for email sending errors")

if __name__ == "__main__":
    test_real_email_flows()