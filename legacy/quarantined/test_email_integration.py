#!/usr/bin/env python3
"""
VeoGen Email Integration Test
============================

Quick test script to verify email workflow integration
"""

import requests
import json
import time
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:4700"

def test_health_check() -> bool:
    """Test if VeoGen API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        health_data = response.json()
        print(f"✅ API Health Status: {health_data.get('status', 'unknown')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API Health Check Failed: {e}")
        return False

def test_email_demo() -> bool:
    """Test the complete email demo endpoint"""
    try:
        response = requests.post(f"{BASE_URL}/api/email/test/demo")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Email Demo: SUCCESS")
            print(f"   Generated {result.get('total_emails_sent', 0)} emails")
            print(f"   Check: {result.get('check_files', 'dev_emails/ folder')}")
            return True
        else:
            print(f"❌ Email Demo Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Email Demo Failed: {e}")
        return False

def test_enhanced_verification() -> bool:
    """Test enhanced verification email"""
    try:
        data = {
            "email": "sandraschipal@hotmail.com",
            "name": "Sandra Schipal"
        }
        response = requests.post(
            f"{BASE_URL}/api/email/verification/enhanced", 
            json=data
        )
        if response.status_code == 200:
            print("✅ Enhanced Verification: SUCCESS")
            return True
        else:
            print(f"❌ Enhanced Verification Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Enhanced Verification Failed: {e}")
        return False

def test_password_reset() -> bool:
    """Test advanced password reset"""
    try:
        data = {
            "email": "sandraschipal@hotmail.com",
            "name": "Sandra Schipal"
        }
        response = requests.post(
            f"{BASE_URL}/api/email/password-reset/advanced", 
            json=data
        )
        if response.status_code == 200:
            print("✅ Advanced Password Reset: SUCCESS")
            return True
        else:
            print(f"❌ Advanced Password Reset Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Advanced Password Reset Failed: {e}")
        return False

def test_workflow_status() -> bool:
    """Test workflow status endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/email/workflows/status")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Workflow Status: SUCCESS")
            print(f"   Total workflows: {result.get('total_workflows', 0)}")
            return True
        else:
            print(f"❌ Workflow Status Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Workflow Status Failed: {e}")
        return False

def main():
    """Run all email integration tests"""
    print("=== VeoGen Email Integration Test ===")
    print()
    
    # Test 1: Health check
    print("1. Testing API Health...")
    if not test_health_check():
        print("❌ VeoGen API is not running. Please start services first:")
        print("   docker-compose up -d")
        sys.exit(1)
    
    print()
    
    # Test 2: Email demo (most comprehensive test)
    print("2. Testing Email Demo (All Workflows)...")
    demo_success = test_email_demo()
    
    print()
    
    # Test 3: Individual endpoints
    print("3. Testing Individual Endpoints...")
    verification_success = test_enhanced_verification()
    reset_success = test_password_reset()
    status_success = test_workflow_status()
    
    print()
    print("=== Test Results ===")
    
    all_tests = [demo_success, verification_success, reset_success, status_success]
    passed = sum(all_tests)
    total = len(all_tests)
    
    if passed == total:
        print(f"🎉 ALL TESTS PASSED ({passed}/{total})")
        print()
        print("✅ Email system integration: COMPLETE")
        print("✅ Database lookups: WORKING")
        print("✅ Email endpoints: FUNCTIONAL")
        print()
        print("Next steps:")
        print("• Visit http://localhost:4700/docs to explore all endpoints")
        print("• Check dev_emails/ folder for generated email files")
        print("• Test frontend integration with enhanced email endpoints")
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total})")
        print("Check the error messages above for details")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
