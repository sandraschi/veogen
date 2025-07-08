#!/usr/bin/env python3
import psycopg2
import bcrypt

# Database connection
DB_URL = "postgresql://veogen:veogen123@localhost:4715/veogen"

def verify_user():
    try:
        # Connect to database
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT email, username, is_active, hashed_password FROM users WHERE email = 'test@test.com'")
        user = cursor.fetchone()
        
        if user:
            print(f"SUCCESS: User found: {user}")
            email, username, is_active, hashed_password = user
            
            # Test password verification
            test_password = 'test123'
            is_valid = bcrypt.checkpw(test_password.encode('utf-8'), hashed_password.encode('utf-8'))
            
            print(f"SUCCESS: Password verification: {is_valid}")
            print(f"   Email: {email}")
            print(f"   Username: {username}")
            print(f"   Is Active: {is_active}")
            print(f"   Hash: {hashed_password}")
            
            if is_valid:
                print("SUCCESS: Password 'test123' is valid for this user!")
            else:
                print("ERROR: Password 'test123' is NOT valid for this user!")
                
        else:
            print("ERROR: User not found!")
            
        conn.close()
        
    except Exception as e:
        print(f"ERROR: Error: {e}")

if __name__ == "__main__":
    verify_user() 