#!/usr/bin/env python3
"""
VeoGen - Quick Onboarding Script for New Claude Sessions
Run this to quickly assess project state and get up to speed
"""
import os
import subprocess
import requests
import json
from pathlib import Path

# Project paths
PROJECT_ROOT = r"C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen"
FRONTEND_URL = "http://localhost:4710"
BACKEND_URL = "http://localhost:4700"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_section(title):
    print(f"\n--- {title} ---")

def run_command(cmd, timeout=10):
    """Run a command and return success status and output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=PROJECT_ROOT)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_file_exists(filepath):
    """Check if important files exist"""
    full_path = Path(PROJECT_ROOT) / filepath
    return full_path.exists()

def test_url(url, name):
    """Test if a URL is accessible"""
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200, response.status_code
    except Exception as e:
        return False, str(e)

def main():
    print_header("VeoGen Project - Quick Onboarding Assessment")
    print(f"Project Root: {PROJECT_ROOT}")
    
    # 1. Check if we're in the right directory
    print_section("1. PROJECT STRUCTURE CHECK")
    if not os.path.exists(PROJECT_ROOT):
        print(f"ERROR: Project directory not found at {PROJECT_ROOT}")
        return
    
    important_files = [
        "README.md",
        "docker-compose.yml", 
        "CLAUDE_RESTART_GUIDE.md",
        "AUTHENTICATION_SUCCESS.md",
        "test_final_auth.py"
    ]
    
    for file in important_files:
        exists = check_file_exists(file)
        status = "OK" if exists else "MISSING"
        print(f"   {status}: {file}")
    
    # 2. Check Docker services
    print_section("2. DOCKER SERVICES STATUS")
    success, stdout, stderr = run_command("docker-compose ps")
    if success:
        print("   Docker Compose Status:")
        for line in stdout.split('\n')[1:]:  # Skip header
            if line.strip():
                print(f"   {line}")
    else:
        print(f"   ERROR: Docker Compose not responding: {stderr}")
        print("   TRY: docker-compose up -d")
    
    # 3. Test service URLs
    print_section("3. SERVICE ACCESSIBILITY")
    services = {
        "Frontend": FRONTEND_URL,
        "Backend API": BACKEND_URL,
        "API Docs": f"{BACKEND_URL}/docs",
        "Health Check": f"{BACKEND_URL}/health"
    }
    
    for name, url in services.items():
        accessible, status = test_url(url, name)
        symbol = "OK" if accessible else "FAIL"
        print(f"   {symbol}: {name} - {url} ({status})")
    
    # 4. Run authentication test if available
    print_section("4. AUTHENTICATION SYSTEM TEST")
    if check_file_exists("test_final_auth.py"):
        success, stdout, stderr = run_command("python test_final_auth.py", timeout=30)
        if success:
            # Extract key information from test output
            lines = stdout.split('\n')
            for line in lines:
                if "SUCCESS:" in line or "ERROR:" in line or "Authentication System Status" in line:
                    print(f"   {line.strip()}")
        else:
            print(f"   ERROR: Auth test failed: {stderr}")
    else:
        print("   WARNING: test_final_auth.py not found")
    
    # 5. Check for recent work documentation
    print_section("5. RECENT WORK STATUS")
    recent_docs = [
        "AUTHENTICATION_SUCCESS.md",
        "AUTH_FIX_SUMMARY.md", 
        "CLAUDE_RESTART_GUIDE.md"
    ]
    
    for doc in recent_docs:
        if check_file_exists(doc):
            print(f"   OK: {doc} - Available for context")
        else:
            print(f"   MISSING: {doc}")
    
    # 6. Quick recommendations
    print_section("6. QUICK START RECOMMENDATIONS")
    
    # Check if services are running
    frontend_ok, _ = test_url(FRONTEND_URL, "frontend")
    backend_ok, _ = test_url(BACKEND_URL, "backend")
    
    if frontend_ok and backend_ok:
        print("   SUCCESS: All core services appear to be running")
        print("   SUCCESS: Ready to continue development")
        print(f"   ACTION: Test login at: {FRONTEND_URL}")
        print("   CREDENTIALS: valid@test.com / Test123!")
    else:
        print("   WARNING: Services may need to be started")
        print("   ACTION: Run: docker-compose up -d")
        print("   ACTION: Wait 30 seconds for services to start")
        print("   ACTION: Re-run this script to verify")
    
    print_section("7. SUGGESTED CLAUDE COMMANDS")
    print('   # Read project context')
    print('   read_file("CLAUDE_RESTART_GUIDE.md")')
    print('   read_file("AUTHENTICATION_SUCCESS.md")')
    print('')
    print('   # Check current status')
    print('   execute_command("docker-compose ps", 10000)')
    print('   execute_command("python test_final_auth.py", 30000)')
    print('')
    print('   # Read key source files')
    print('   read_file("frontend/src/contexts/AuthContext.js")')
    print('   read_file("backend/app/api/api_v1/endpoints/enhanced_auth.py")')
    
    print_header("ONBOARDING COMPLETE")
    if frontend_ok and backend_ok:
        print("SUCCESS: VeoGen appears to be healthy and ready for work!")
        print("NEXT: Read CLAUDE_RESTART_GUIDE.md for full context")
    else:
        print("WARNING: Services need attention - follow troubleshooting steps above")

if __name__ == "__main__":
    main()
