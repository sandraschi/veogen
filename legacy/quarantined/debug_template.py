#!/usr/bin/env python3
"""
Debug the password reset email template generation
"""

import sys
import os
sys.path.append('/app')  # Add to Docker path

def test_template_generation():
    print("Testing password reset template generation...")
    
    # Import the template function
    try:
        from app.services.email_templates import get_password_reset_template
        
        # Test with the same parameters that would be used
        user_name = "sas13"
        reset_url = "http://localhost:4710/reset-password?token=TEST_TOKEN&user=TEST_USER"
        
        subject, text_body, html_body = get_password_reset_template(user_name, reset_url)
        
        print(f"Subject: {subject}")
        print(f"Text body:\n{text_body}")
        print(f"HTML body length: {len(html_body)} chars")
        
        # Check if the URL is correct in the template
        if "localhost:4710" in text_body:
            print("✅ URL is correct in template")
        else:
            print("❌ URL is wrong in template")
            
        if "yourdomain.com" in text_body:
            print("❌ Found yourdomain.com in template!")
        else:
            print("✅ No yourdomain.com found")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_template_generation()
