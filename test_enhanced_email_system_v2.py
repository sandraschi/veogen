"""
VeoGen Enhanced Email System Test Script v2.0
============================================

Comprehensive test script for the enhanced email workflow system
"""

import asyncio
import sys
import os
import json
import requests
from datetime import datetime
from typing import Dict, Any

# Configuration
BACKEND_URL = "http://localhost:4700"
EMAIL_API_BASE = f"{BACKEND_URL}/api/email"

def print_section(title: str, emoji: str = "🔧"):
    """Print formatted section header"""
    print(f"\n{emoji} {title}")
    print("=" * (len(title) + 4))

def print_result(success: bool, message: str, data: Dict[str, Any] = None):
    """Print formatted test result"""
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"   {status}: {message}")
    if data:
        print(f"   Data: {json.dumps(data, indent=6)}")

async def test_backend_connection():
    """Test backend connectivity"""
    print_section("Backend Connection Test", "🔌")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print_result(True, "Backend is healthy and responding")
            return True
        else:
            print_result(False, f"Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Cannot connect to backend: {e}")
        return False

async def test_email_system_health():
    """Test email system health endpoint"""
    print_section("Email System Health Check", "🏥")
    
    try:
        response = requests.get(f"{EMAIL_API_BASE}/test/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print_result(True, "Email system is healthy")
            print(f"   Version: {health_data.get('version')}")
            print(f"   Features: {len(health_data.get('features', {}))} available")
            return True
        else:
            print_result(False, f"Email health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Email health check error: {e}")
        return False

async def test_enhanced_registration():
    """Test enhanced registration email workflow"""
    print_section("Enhanced Registration Workflow", "📧")
    
    test_data = {
        "email": "sandraschipal@hotmail.com",
        "name": "Sandra Schipal",
        "user_id": "user_test_123",
        "send_welcome_series": True
    }
    
    try:
        response = requests.post(
            f"{EMAIL_API_BASE}/registration/enhanced",
            json=test_data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print_result(True, "Enhanced registration email sent")
            print_result(True, f"Workflow ID: {result['workflow_id']}")
            return result['workflow_id']
        else:
            print_result(False, f"Registration email failed: {response.status_code}")
            return None
            
    except Exception as e:
        print_result(False, f"Registration email error: {e}")
        return None

async def test_security_challenge():
    """Test security challenge workflow"""
    print_section("Security Challenge Workflow", "🔐")
    
    challenge_data = {
        "user_id": "user_test_123",
        "action": "Delete Account"
    }
    
    try:
        response = requests.post(
            f"{EMAIL_API_BASE}/challenge/initiate",
            json=challenge_data,
            headers={"User-Agent": "VeoGen-Test/1.0"},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            challenge_id = result['challenge_id']
            print_result(True, "Security challenge initiated")
            print_result(True, f"Challenge ID: {challenge_id}")
            
            # Test verification with mock code
            verify_data = {
                "challenge_id": challenge_id,
                "challenge_code": "123456"
            }
            
            verify_response = requests.post(
                f"{EMAIL_API_BASE}/challenge/verify",
                json=verify_data,
                timeout=10
            )
            
            if verify_response.status_code == 200:
                verify_result = verify_response.json()
                print_result(verify_result['valid'], "Challenge verification test")
            
            return challenge_id
        else:
            print_result(False, f"Security challenge failed: {response.status_code}")
            return None
            
    except Exception as e:
        print_result(False, f"Security challenge error: {e}")
        return None

async def test_video_notification():
    """Test video ready notification"""
    print_section("Video Ready Notification", "🎬")
    
    video_data = {
        "user_id": "user_test_123",
        "video_title": "Sunset Over Mountain Lake - Enhanced Test",
        "video_id": "video_test_456",
        "duration": 45,
        "resolution": "4K"
    }
    
    try:
        response = requests.post(
            f"{EMAIL_API_BASE}/notification/video-ready",
            json=video_data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print_result(True, "Video notification sent")
            print_result(True, f"Video: {video_data['video_title']}")
            return result['workflow_id']
        else:
            print_result(False, f"Video notification failed: {response.status_code}")
            return None
            
    except Exception as e:
        print_result(False, f"Video notification error: {e}")
        return None

async def test_weekly_digest():
    """Test weekly digest email"""
    print_section("Weekly Digest Email", "📊")
    
    digest_data = {
        "user_id": "user_test_123",
        "videos_created": 12,
        "total_duration": 680,
        "days_active": 6
    }
    
    try:
        response = requests.post(
            f"{EMAIL_API_BASE}/digest/weekly",
            json=digest_data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print_result(True, "Weekly digest sent")
            return result['workflow_id']
        else:
            print_result(False, f"Weekly digest failed: {response.status_code}")
            return None
            
    except Exception as e:
        print_result(False, f"Weekly digest error: {e}")
        return None

async def test_security_alert():
    """Test security alert notification"""
    print_section("Security Alert Notification", "🚨")
    
    alert_data = {
        "user_id": "user_test_123",
        "activity_type": "Suspicious login attempt from new device",
        "ip_address": "203.0.113.42",
        "location": "Unknown Location",
        "device_info": "Chrome 127.0 on Windows 11",
        "risk_level": "High"
    }
    
    try:
        response = requests.post(
            f"{EMAIL_API_BASE}/security/alert",
            json=alert_data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print_result(True, "Security alert sent")
            return result['workflow_id']
        else:
            print_result(False, f"Security alert failed: {response.status_code}")
            return None
            
    except Exception as e:
        print_result(False, f"Security alert error: {e}")
        return None

async def test_email_analytics():
    """Test email analytics endpoint"""
    print_section("Email Analytics", "📊")
    
    try:
        response = requests.get(f"{EMAIL_API_BASE}/analytics", timeout=10)
        
        if response.status_code == 200:
            analytics = response.json()
            print_result(True, "Analytics retrieved successfully")
            print(f"   Open rate: {analytics.get('open_rate', 0):.1f}%")
            print(f"   Click rate: {analytics.get('click_rate', 0):.1f}%")
            return True
        else:
            print_result(False, f"Analytics request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Analytics error: {e}")
        return False

async def test_demo_workflow():
    """Test the demo workflow endpoint"""
    print_section("Demo All Workflows", "🎪")
    
    try:
        response = requests.post(f"{EMAIL_API_BASE}/test/demo-all", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print_result(True, "Demo workflows executed successfully")
            print(f"   Workflows tested: {result.get('total_workflows', 0)}")
            return True
        else:
            print_result(False, f"Demo workflows failed: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Demo workflows error: {e}")
        return False

async def check_email_files():
    """Check if email files were generated"""
    print_section("Email Files Check", "📁")
    
    dev_emails_dir = "dev_emails"
    
    try:
        if os.path.exists(dev_emails_dir):
            email_files = [f for f in os.listdir(dev_emails_dir) if f.endswith(('.eml', '.html'))]
            print_result(True, f"Email files directory exists")
            print(f"   Email files: {len(email_files)} (.eml and .html)")
            
            if email_files:
                print("   Recent email files:")
                for file in sorted(email_files)[-3:]:
                    print(f"     • {file}")
            
            return len(email_files) > 0
        else:
            print_result(False, "Email files directory not found")
            return False
            
    except Exception as e:
        print_result(False, f"Email files check error: {e}")
        return False

async def run_comprehensive_test():
    """Run comprehensive test of all email workflows"""
    
    print("🚀 VeoGen Enhanced Email System v2.0 - Comprehensive Test")
    print("=" * 70)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {}
    
    # Core tests
    test_results['backend_connection'] = await test_backend_connection()
    test_results['email_health'] = await test_email_system_health()
    
    # Email workflow tests
    test_results['registration'] = await test_enhanced_registration()
    test_results['security_challenge'] = await test_security_challenge()
    test_results['video_notification'] = await test_video_notification()
    test_results['weekly_digest'] = await test_weekly_digest()
    test_results['security_alert'] = await test_security_alert()
    
    # Analytics tests
    test_results['analytics'] = await test_email_analytics()
    
    # Demo and file tests
    test_results['demo_workflow'] = await test_demo_workflow()
    test_results['email_files'] = await check_email_files()
    
    # Summary
    print_section("Test Summary", "📊")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"   Total tests: {total_tests}")
    print(f"   Passed: {passed_tests} ✅")
    print(f"   Failed: {failed_tests} ❌")
    print(f"   Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print("\n❌ Failed tests:")
        for test_name, result in test_results.items():
            if not result:
                print(f"   • {test_name}")
    
    print_section("Next Steps", "🎯")
    
    if passed_tests == total_tests:
        print("   🎉 All tests passed! VeoGen Enhanced Email System is ready for production.")
        print("   ✅ Integration: Add email_router to your FastAPI main app")
        print("   ✅ Database: Update user lookup functions with real database calls")
        print("   ✅ Frontend: Integrate email workflows with your UI components")
    else:
        print("   🔧 Some tests failed. Please check the errors above.")
    
    print(f"\n📁 Email files saved to: {os.path.abspath('dev_emails')}")
    print(f"📊 View email templates: Open .html files in browser")
    
    print("\n" + "=" * 70)
    print("🎬 VeoGen Enhanced Email System v2.0 Test Complete!")
    print("=" * 70)
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_test())
    sys.exit(0 if success else 1)
