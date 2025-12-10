#!/usr/bin/env python3
"""
Test VeoGen Email System - Password Reset and Email Verification
"""
import requests
import json
import time
import os

def test_email_system():
    print("=== VeoGen Email System Test ===")
    print()
    
    # Test password reset with Sandra's account
    print("1. Testing Password Reset Email Generation")
    try:
        reset_response = requests.post(
            'http://localhost:4700/api/v1/enhanced-auth/request-password-reset', 
            json={'email': 'sandraschipal@hotmail.com'}
        )
        
        print(f"   Status: {reset_response.status_code}")
        print(f"   Response: {reset_response.text}")
        
        if reset_response.status_code == 200:
            print("   SUCCESS: Password reset request sent!")
        else:
            print(f"   FAILED: {reset_response.text}")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print()
    
    # Test with valid test account
    print("2. Testing Password Reset with Test Account")
    try:
        reset_response = requests.post(
            'http://localhost:4700/api/v1/enhanced-auth/request-password-reset', 
            json={'email': 'valid@test.com'}
        )
        
        print(f"   Status: {reset_response.status_code}")
        print(f"   Response: {reset_response.text}")
        
        if reset_response.status_code == 200:
            print("   SUCCESS: Password reset request sent!")
        else:
            print(f"   FAILED: {reset_response.text}")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print()
    
    # Check if emails were generated
    print("3. Checking Generated Email Files")
    dev_emails_path = "backend/dev_emails"
    
    if os.path.exists(dev_emails_path):
        files = os.listdir(dev_emails_path)
        print(f"   Found {len(files)} email files:")
        
        for file in files:
            print(f"   - {file}")
            
        if files:
            # Read the latest email
            latest_file = sorted(files)[-1]
            print(f"\n   Reading latest email: {latest_file}")
            
            try:
                with open(os.path.join(dev_emails_path, latest_file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    print("   --- EMAIL CONTENT ---")
                    print(content[:500] + "..." if len(content) > 500 else content)
                    print("   --- END EMAIL ---")
            except Exception as e:
                print(f"   Error reading email: {e}")
        else:
            print("   No email files found - emails may not be generating")
    else:
        print("   dev_emails directory doesn't exist")
    
    print()
    
    # Test email verification endpoint
    print("4. Testing Email Verification Endpoint")
    try:
        # Test with dummy token
        verify_response = requests.post(
            'http://localhost:4700/api/v1/enhanced-auth/verify-email',
            json={'token': 'dummy_token_for_testing'}
        )
        
        print(f"   Status: {verify_response.status_code}")
        print(f"   Response: {verify_response.text}")
        
        # This should fail, but the endpoint should exist
        if verify_response.status_code in [400, 404]:
            print("   SUCCESS: Verification endpoint exists (expected failure with dummy token)")
        else:
            print("   INFO: Unexpected response")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print()
    
    # Test resend verification
    print("5. Testing Resend Verification Email")
    try:
        resend_response = requests.post(
            'http://localhost:4700/api/v1/enhanced-auth/resend-verification',
            json={'email': 'valid@test.com'}
        )
        
        print(f"   Status: {resend_response.status_code}")
        print(f"   Response: {resend_response.text}")
        
        if resend_response.status_code == 200:
            print("   SUCCESS: Verification email resent!")
        else:
            print(f"   INFO: {resend_response.text}")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print()
    print("=== Email System Test Complete ===")
    
    # Final check of email files
    if os.path.exists(dev_emails_path):
        files = os.listdir(dev_emails_path)
        print(f"Final count: {len(files)} email files generated")
    
    return True

if __name__ == "__main__":
    test_email_system()
