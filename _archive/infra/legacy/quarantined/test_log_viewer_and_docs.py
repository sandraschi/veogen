#!/usr/bin/env python3
"""
Test Log Viewer and Docsify Docs Viewer
Tests both components to ensure they're working properly
"""

import requests
import json
import sys
from datetime import datetime

def test_log_viewer_api():
    """Test the log viewer API endpoint"""
    print("Testing Log Viewer API...")
    
    try:
        # Need to authenticate first
        auth_response = requests.post(
            "http://localhost:4700/api/v1/auth/login",
            json={
                "email": "valid@test.com",
                "password": "Test123!"
            }
        )
        
        if auth_response.status_code == 200:
            token = auth_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test logs endpoint with authentication
            logs_response = requests.get(
                "http://localhost:4700/api/v1/logs/",
                headers=headers
            )
            
            if logs_response.status_code == 200:
                data = logs_response.json()
                print(f"  SUCCESS: Logs API working - {len(data.get('logs', []))} logs returned")
                print(f"  Components: {data.get('available_components', [])}")
                print(f"  Levels: {data.get('available_levels', [])}")
                return True
            else:
                print(f"  FAILED: Logs API failed - {logs_response.status_code}")
                print(f"  Response: {logs_response.text[:200]}...")
                return False
        else:
            print(f"  FAILED: Authentication failed - {auth_response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def test_docsify_docs():
    """Test the docsify documentation viewer"""
    print("\nTesting Docsify Docs Viewer...")
    
    try:
        # Test main docs page at /documentation
        response = requests.get("http://localhost:4700/documentation/")
        
        if response.status_code == 200:
            content = response.text
            if "docsify" in content.lower() and "veogen" in content.lower():
                print("  SUCCESS: Docsify docs accessible")
                print(f"  Page size: {len(content)} characters")
                
                # Check for key elements
                checks = [
                    ("Theme toggle", "themeToggle" in content),
                    ("Console", "console" in content.lower()),
                    ("Search", "search" in content.lower()),
                    ("Sidebar", "sidebar" in content.lower()),
                ]
                
                for check_name, check_result in checks:
                    status = "FOUND" if check_result else "MISSING"
                    print(f"  {check_name}: {status}")
                
                return all(check[1] for check in checks)
            else:
                print("  FAILED: Docsify content not found")
                return False
        else:
            print(f"  FAILED: Docsify docs not accessible - {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def test_backend_health():
    """Test backend health"""
    print("Testing Backend Health...")
    
    try:
        response = requests.get("http://localhost:4700/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  SUCCESS: Backend healthy - {data.get('status', 'unknown')}")
            return True
        else:
            print(f"  FAILED: Backend unhealthy - {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("VeoGen Log Viewer and Docsify Tests")
    print("=" * 50)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Log Viewer API", test_log_viewer_api),
        ("Docsify Docs", test_docsify_docs),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status} - {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("SUCCESS: All tests passed!")
        print("Main App: http://localhost:4710")
        print("API Documentation: http://localhost:4700/docs")
        print("Project Documentation: http://localhost:4700/documentation")
    else:
        print("WARNING: Some tests failed.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
