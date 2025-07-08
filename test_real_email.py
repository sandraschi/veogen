#!/usr/bin/env python3
"""
Test REAL EMAIL SENDING for VeoGen!
"""
import requests
import json

def test_real_email_sending():
    print("TESTING REAL EMAIL SENDING!")
    print("="*50)
    
    # Test password reset to Sandra's own email
    print("Sending password reset email to sandraschipal@hotmail.com")
    
    try:
        response = requests.post(
            'http://localhost:4700/api/v1/enhanced-auth/request-password-reset',
            json={'email': 'sandraschipal@hotmail.com'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("\nSUCCESS! Password reset email sent!")
            print("\nCHECK YOUR EMAIL INBOX NOW!")
            print("   -> sandraschipal@hotmail.com")
            print("   -> Look for email from: sandraschipal@hotmail.com")
            print("   -> Subject: VeoGen Password Reset Request")
            print("   -> Beautiful HTML email with reset link!")
        else:
            print(f"\nFailed: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50)
    print("If you received the email - REAL EMAIL SYSTEM IS WORKING!")

if __name__ == "__main__":
    test_real_email_sending()
