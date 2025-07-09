#!/usr/bin/env python3
"""
VeoGen User Manager - Smart Startup Script
Automatically checks dependencies and starts the User Manager
"""
import subprocess
import sys
import time
import requests
import psycopg2
import os

def run_command(command, timeout=30):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_docker():
    """Check if Docker is running"""
    print("🐳 Checking Docker status...")
    success, stdout, stderr = run_command("docker ps")
    if success:
        print("✅ Docker is running")
        return True
    else:
        print("❌ Docker is not running")
        print("   Please start Docker Desktop first!")
        return False

def check_veogen_services():
    """Check if VeoGen services are running"""
    print("🔍 Checking VeoGen services...")
    
    # Check if containers are running
    success, stdout, stderr = run_command("docker-compose ps")
    if not success:
        print("❌ Docker Compose not available")
        return False
    
    # Check if services are responding
    try:
        response = requests.get("http://localhost:4700/health", timeout=5)
        print("✅ VeoGen Backend is running")
    except:
        print("❌ VeoGen Backend not responding")
        return False
    
    # Check PostgreSQL
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=4715,
            database='veogen',
            user='veogen',
            password='veogen123'
        )
        conn.close()
        print("✅ PostgreSQL database is accessible")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL not accessible: {e}")
        return False

def start_veogen_services():
    """Start VeoGen services"""
    print("🚀 Starting VeoGen services...")
    success, stdout, stderr = run_command("docker-compose up -d", timeout=60)
    if success:
        print("✅ VeoGen services started")
        # Wait for services to be ready
        print("⏳ Waiting for services to be ready...")
        time.sleep(20)
        return True
    else:
        print(f"❌ Failed to start services: {stderr}")
        return False

def start_user_manager():
    """Start the User Manager server"""
    print("🎭 Starting User Manager server...")
    print("   Server will start on http://localhost:8083")
    print("   Press Ctrl+C to stop")
    
    # Change to the correct directory
    os.chdir(r"C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen")
    
    # Start the server
    try:
        subprocess.run([sys.executable, "user_manager_server.py"])
    except KeyboardInterrupt:
        print("\n👋 User Manager stopped")

def main():
    """Main startup sequence"""
    print("🎭 VeoGen User Manager - Smart Startup")
    print("=" * 50)
    
    # Step 1: Check Docker
    if not check_docker():
        sys.exit(1)
    
    # Step 2: Check VeoGen services
    if not check_veogen_services():
        print("\n🚀 VeoGen services not running - starting them...")
        if not start_veogen_services():
            sys.exit(1)
        
        # Recheck after starting
        if not check_veogen_services():
            print("❌ Services still not ready after startup")
            sys.exit(1)
    
    print("\n✅ All dependencies ready!")
    print("=" * 50)
    
    # Step 3: Start User Manager
    start_user_manager()

if __name__ == "__main__":
    main()
