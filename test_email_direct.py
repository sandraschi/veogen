#!/usr/bin/env python3
"""
Test email service directly
"""
import sys
import os

# Add backend path to sys.path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from app.services.email_service import send_email

def test_email_service():
    print("=== Direct Email Service Test ===")
    
    # Test email generation
    to = "test@example.com"
    subject = "Test Email"
    body = "This is a test email from VeoGen"
    html = "<p>This is a <strong>test email</strong> from VeoGen</p>"
    
    print(f"Testing email to: {to}")
    print(f"Subject: {subject}")
    
    result = send_email(to, subject, body, html)
    
    if result:
        print("SUCCESS: Email function returned True")
    else:
        print("FAILED: Email function returned False")
    
    # Check if file was created
    print("\nChecking for email files in backend/dev_emails/...")
    dev_emails_path = os.path.join(os.path.dirname(__file__), 'backend', 'dev_emails')
    
    if os.path.exists(dev_emails_path):
        files = os.listdir(dev_emails_path)
        print(f"Found {len(files)} email files:")
        for file in files:
            print(f"  - {file}")
            
        # Show content of most recent file
        if files:
            latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(dev_emails_path, f)))
            file_path = os.path.join(dev_emails_path, latest_file)
            print(f"\nContent of latest email ({latest_file}):")
            print("-" * 50)
            with open(file_path, 'r', encoding='utf-8') as f:
                print(f.read())
            print("-" * 50)
    else:
        print("dev_emails directory not found")

if __name__ == "__main__":
    test_email_service()
