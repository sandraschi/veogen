#!/usr/bin/env python3
"""
Debug the email template generation
"""
import sys
import os

# Add the backend app to the path
sys.path.append("/app")
sys.path.append("backend/app")

# Try to import and test the email templates
try:
    from app.services.email_templates import get_password_reset_template
    
    print("=== Testing Email Template Function ===")
    
    # Test the password reset template
    user_name = "TestUser"
    reset_url = "http://localhost:4710/reset-password?token=test123&user=test456"
    
    subject, text_body, html_body = get_password_reset_template(user_name, reset_url)
    
    print(f"Subject: {subject}")
    print(f"Text body (first 200 chars): {text_body[:200]}...")
    print(f"HTML body exists: {bool(html_body)}")
    if html_body:
        print(f"HTML body (first 200 chars): {html_body[:200]}...")
    
    print("\n=== Testing send_email function ===")
    from app.services.email_service import send_email
    
    # Test email generation
    send_email("debug@test.com", subject, text_body, html_body)
    print("Email sent successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
