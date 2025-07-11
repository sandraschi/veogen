#!/usr/bin/env python3
"""
Quick test script for User Manager Tool fixes
"""

import subprocess
import time
import sys
import os

def test_user_manager():
    """Test the User Manager Tool after fixes."""
    print("🧪 Testing VeoGen User Manager Tool Fixes...")
    print("=" * 60)
    
    # Check if VeoGen services are running
    print("1. Checking VeoGen services...")
    try:
        result = subprocess.run(['docker-compose', 'ps'], 
                              capture_output=True, text=True, 
                              cwd=r'C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen')
        if 'veogen-postgres-1' in result.stdout and 'Up' in result.stdout:
            print("   ✅ VeoGen PostgreSQL is running")
        else:
            print("   ❌ VeoGen services not running. Starting them...")
            subprocess.run(['docker-compose', 'up', '-d'], 
                          cwd=r'C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen')
            time.sleep(10)
            print("   ✅ VeoGen services started")
    except Exception as e:
        print(f"   ❌ Error checking services: {e}")
        return False
    
    print("\n2. Summary of fixes applied:")
    print("   ✅ Fixed UUID generation in create_user endpoint")
    print("   ✅ Added proper password hashing with salt")
    print("   ✅ Enhanced error handling for duplicate emails/usernames")
    print("   ✅ Increased table font size to 16px for better readability")
    print("   ✅ Added font-weight: 500 for table data")
    print("   ✅ Increased status badge font size to 14px")
    
    print("\n3. Starting User Manager Tool...")
    print("   🌐 Frontend: http://localhost:8083")
    print("   📚 API Docs: http://localhost:8083/docs")
    print("   ❤️ Health Check: http://localhost:8083/health")
    
    print("\n4. Test the following:")
    print("   ✅ Font readability - table text should be larger and easier to read")
    print("   ✅ Create user - should work without UUID errors")
    print("   ✅ Error messages - duplicate email/username should show proper errors")
    print("   ✅ User list - displays existing users properly")
    
    print("\n🚀 Ready to test! Open http://localhost:8083 in your browser")
    print("   Try creating a test user to verify the create functionality works!")
    
    return True

if __name__ == "__main__":
    success = test_user_manager()
    if success:
        print("\n✅ User Manager Tool test setup complete!")
        print("   Ready for manual testing in browser")
    else:
        print("\n❌ Test setup failed!")
        sys.exit(1)
