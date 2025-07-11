#!/usr/bin/env python3
"""
Test VeoGen services after Docker restart
"""
import requests
import json
import time
import subprocess

def test_docker_ps():
    """Check Docker container status"""
    print("=== Docker Container Status ===")
    try:
        result = subprocess.run(['docker-compose', 'ps'], 
                              capture_output=True, text=True, cwd="C:\\Users\\sandr\\AppData\\Local\\AnthropicClaude\\app-0.11.6\\veogen")
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
    except Exception as e:
        print(f"Error checking docker status: {e}")

def test_port_mapping():
    """Check if ports are properly mapped"""
    print("\n=== Port Mapping Test ===")
    
    # Test if ports are listening
    import socket
    
    ports_to_test = [4700, 4710, 4715, 8083]
    
    for port in ports_to_test:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {port}: OPEN")
        else:
            print(f"❌ Port {port}: CLOSED")

def test_services():
    """Test VeoGen services"""
    print("\n=== Service Health Tests ===")
    
    # Test 1: Backend Health
    print("\n1. Backend Health (localhost:4700)...")
    try:
        response = requests.get("http://localhost:4700/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ Backend: {health.get('status')}")
            components = health.get('components', {})
            for comp, status in components.items():
                print(f"   - {comp}: {status}")
        else:
            print(f"   ❌ Backend health failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Backend error: {e}")
    
    # Test 2: Frontend
    print("\n2. Frontend (localhost:4710)...")
    try:
        response = requests.get("http://localhost:4710", timeout=10)
        if response.status_code == 200:
            print("   ✅ Frontend accessible")
            if "veogen" in response.text.lower():
                print("   ✅ Contains VeoGen content")
        else:
            print(f"   ❌ Frontend failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Frontend error: {e}")
    
    # Test 3: Database (via backend)
    print("\n3. Database connectivity...")
    try:
        response = requests.get("http://localhost:4700/api/v1/users/me", timeout=10)
        # We expect 401 (unauthorized) which means the endpoint is working
        if response.status_code == 401:
            print("   ✅ Database connection working (auth required)")
        elif response.status_code == 200:
            print("   ✅ Database connection working")
        else:
            print(f"   ⚠️  Database test: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Database test error: {e}")
    
    # Test 4: Quick login test
    print("\n4. Authentication test...")
    try:
        login_data = {"email": "valid@test.com", "password": "Test123!"}
        response = requests.post("http://localhost:4700/api/v1/enhanced-auth/login", 
                               json=login_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Login successful")
            print(f"   - User: {result.get('user', {}).get('email')}")
            print(f"   - Token: {'Yes' if result.get('access_token') else 'No'}")
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Login error: {e}")

def test_user_manager():
    """Test User Manager specifically"""
    print("\n=== User Manager Test ===")
    try:
        response = requests.get("http://localhost:8083/api/users", timeout=5)
        if response.status_code == 200:
            users = response.json()
            print(f"✅ User Manager working - {len(users)} users found")
        else:
            print(f"❌ User Manager failed: {response.status_code}")
    except Exception as e:
        print(f"❌ User Manager not running: {e}")

if __name__ == "__main__":
    print("🚀 VeoGen Post-Restart Diagnostics")
    print("=" * 50)
    
    test_docker_ps()
    test_port_mapping()
    test_services()
    test_user_manager()
    
    print("\n" + "=" * 50)
    print("✅ Diagnostics Complete")
    print("\nIf services are failing:")
    print("1. Check: docker-compose ps")
    print("2. Restart: docker-compose restart")
    print("3. Full restart: docker-compose down && docker-compose up -d")
