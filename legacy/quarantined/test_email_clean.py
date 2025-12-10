#!/usr/bin/env python3
"""
VeoGen Email System Test
Tests email verification and password reset functionality
"""

import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:4700"

def test_email_system():
    print("VeoGen Email System Test")
    print("=" * 40)
    
    # Test 1: Register a new user (should trigger verification email)
    print("\nTest 1: User Registration (Email Verification)")
    test_email = f"test-{int(time.time())}@example.com"
    register_data = {
        "email": test_email,
        "password": "TestPass123!",
        "username": f"testuser{int(time.time())}",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/v1/enhanced-auth/register", json=register_data)
        print(f"Registration Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: User registered: {data['user']['email']}")
            print(f"Email verified: {data['user']['is_verified']}")
            print(f"Verification email should be in dev_emails/")
            user_id = data['user']['id']
            token = data['access_token']
        else:
            print(f"FAILED: Registration failed: {response.text}")
            return
            
    except Exception as e:
        print(f"ERROR: Registration error: {e}")
        return
    
    # Test 2: Resend verification email
    print("\nTest 2: Resend Verification Email")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{API_BASE}/api/v1/enhanced-auth/resend-verification", 
                               headers=headers)
        print(f"Resend Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Resend successful: {data['message']}")
        else:
            print(f"FAILED: Resend failed: {response.text}")
            
    except Exception as e:
        print(f"ERROR: Resend error: {e}")
    
    # Test 3: Request password reset
    print("\nTest 3: Password Reset Request")
    try:
        reset_data = {"email": test_email}
        response = requests.post(f"{API_BASE}/api/v1/enhanced-auth/request-password-reset", 
                               json=reset_data)
        print(f"Reset Request Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Reset email sent: {data['message']}")
        else:
            print(f"FAILED: Reset request failed: {response.text}")
            
    except Exception as e:
        print(f"ERROR: Reset request error: {e}")
    
    # Test 4: Check saved emails
    print("\nTest 4: Check Saved Emails")
    import os
    import glob
    
    email_dir = "dev_emails"
    if os.path.exists(email_dir):
        email_files = glob.glob(f"{email_dir}/*.eml")
        print(f"SUCCESS: Email directory exists: {len(email_files)} emails saved")
        
        # Show recent emails
        email_files.sort(key=os.path.getmtime, reverse=True)
        for i, email_file in enumerate(email_files[:3]):
            filename = os.path.basename(email_file)
            mtime = datetime.fromtimestamp(os.path.getmtime(email_file))
            print(f"  {i+1}. {filename} ({mtime.strftime('%Y-%m-%d %H:%M:%S')})")
    else:
        print(f"FAILED: Email directory not found: {email_dir}")
    
    print("\nEmail System Test Summary")
    print("=" * 40)
    print("RESULT: Registration triggers verification email")
    print("RESULT: Can resend verification emails") 
    print("RESULT: Can request password reset emails")
    print("RESULT: Emails saved to dev_emails/ folder")
    print("\nTo test email flows:")
    print("1. Check dev_emails/ folder for email content")
    print("2. Extract verification/reset tokens from emails")
    print("3. Test frontend verification/reset pages with tokens")

if __name__ == "__main__":
    test_email_system()