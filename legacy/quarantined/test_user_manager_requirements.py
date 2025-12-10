#!/usr/bin/env python3
"""
Quick test to check VeoGen services and User Manager requirements
"""
import requests
import psycopg2
import sys

def test_veogen_services():
    """Test if VeoGen services are running"""
    print("🔍 Testing VeoGen Services Status...")
    
    # Test Backend
    try:
        response = requests.get("http://localhost:4700/health", timeout=5)
        print(f"✅ VeoGen Backend: {response.status_code}")
    except Exception as e:
        print(f"❌ VeoGen Backend: NOT RUNNING - {e}")
        return False
    
    # Test Frontend
    try:
        response = requests.get("http://localhost:4710", timeout=5)
        print(f"✅ VeoGen Frontend: {response.status_code}")
    except Exception as e:
        print(f"❌ VeoGen Frontend: NOT RUNNING - {e}")
    
    # Test PostgreSQL Database
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=4715,
            database='veogen',
            user='veogen',
            password='veogen123'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"✅ PostgreSQL Database: Connected - {user_count} users found")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL Database: NOT AVAILABLE - {e}")
        print("\n🚨 SOLUTION: Start VeoGen services first!")
        print("Run: cd C:\\Users\\sandr\\AppData\\Local\\AnthropicClaude\\app-0.11.6\\veogen")
        print("Run: docker-compose up -d")
        return False

if __name__ == "__main__":
    if test_veogen_services():
        print("\n✅ All services OK - User Manager should work!")
        print("Now run: python user_manager_server.py")
    else:
        print("\n❌ Services not ready - Fix the issues above first")
        sys.exit(1)
