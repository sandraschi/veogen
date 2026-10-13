#!/usr/bin/env python3
"""
Simple script to create a test user with a known password
"""
import bcrypt
import psycopg2

# Database connection
DB_URL = "postgresql://veogen:veogen123@localhost:4715/veogen"

def create_test_user():
    try:
        # Connect to database
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # Create password hash for 'test123'
        password = 'test123'
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
        
        # Insert test user
        cursor.execute("""
            INSERT INTO users (id, email, username, hashed_password, is_active, is_verified, plan, full_name) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
            ON CONFLICT (email) DO UPDATE SET 
                hashed_password = EXCLUDED.hashed_password,
                is_active = EXCLUDED.is_active
        """, (
            'test_user',
            'test@test.com', 
            'testuser',
            hashed,
            True,
            True,
            'admin',
            'Test User'
        ))
        
        conn.commit()
        print("SUCCESS: Created test user:")
        print("   Email: test@test.com")
        print(f"   Password: {password}")
        print(f"   Hash: {hashed}")
        
        # Verify the user was created
        cursor.execute("SELECT email, username, is_active FROM users WHERE email = 'test@test.com'")
        user = cursor.fetchone()
        if user:
            print(f"SUCCESS: User verified in database: {user}")
        else:
            print("ERROR: User not found in database")
            
        conn.close()
        
    except Exception as e:
        print(f"ERROR: Error creating test user: {e}")

if __name__ == "__main__":
    create_test_user() 